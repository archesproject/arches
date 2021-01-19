import json
import logging
import os
import requests
import shutil
import uuid
from revproxy.views import ProxyView
from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.search import search_results


logger = logging.getLogger(__name__)


class ManifestManagerView(View):
    def delete(self, request):
        data = JSONDeserializer().deserialize(request.body)
        manifest = data.get("manifest")
        manifest = models.IIIFManifest.objects.get(url=manifest)
        manifest.delete()
        return JSONResponse({"success": True})

    def post(self, request):
        self.iiif_proxy_uri = request.scheme + "://" + request.get_host() + "/iiifserver/"

        def create_manifest(
            name="<manifest_title>", desc="<manifest_description>", file_url="file_url", attribution="", logo="", canvases=[]
        ):
            metadata = []  # {"label": "TBD", "value": ["Unknown", ...]}
            sequence_id = settings.CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/sequence/TBD.json"

            return {
                "@context": "http://iiif.io/api/presentation/2/context.json",
                "@type": "sc:Manifest",
                "description": desc,
                "label": name,
                "attribution": attribution,
                "logo": logo,
                "metadata": metadata,
                "thumbnail": {
                    "@id": file_url + "/full/!300,300/0/default.jpg",
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "label": "Main View (.45v)",
                },
                "sequences": [
                    {
                        "@id": sequence_id,
                        "@type": "sc:Sequence",
                        "canvases": canvases,
                        "label": "Object",
                        "startCanvas": "",
                    }
                ],
            }

        def create_canvas(image_json, file_url, file_name, image_id):
            canvas_id = f"{settings.CANTALOUPE_HTTP_ENDPOINT}iiif/manifest/canvas/{image_id}.json"
            image_id = f"{settings.CANTALOUPE_HTTP_ENDPOINT}iiif/manifest/annotation/{image_id}.json"

            return {
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "height": image_json["height"],
                "width": image_json["width"],
                "images": [
                    {
                        "@id": image_id,
                        "@type": "oa.Annotation",
                        "motivation": "unknown",
                        "on": canvas_id,
                        "resource": {
                            "@id": file_url + "/full/full/0/default.jpg",
                            "@type": "dctypes:Image",
                            "format": "image/jpeg",
                            "height": image_json["height"],
                            "width": image_json["width"],
                            "service": {
                                "@context": "http://iiif.io/api/image/2/context.json",
                                "@id": file_url,
                                "profile": "http://iiif.io/api/image/2/level2.json",
                            },
                        },
                    }
                ],
                "label": f"{file_name}",
                "license": "TBD",
                "thumbnail": {
                    "@id": file_url + "/full/!300,300/0/default.jpg",
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "service": {
                        "@context": "http://iiif.io/api/image/2/context.json",
                        "@id": file_url,
                        "profile": "http://iiif.io/api/image/2/level2.json",
                    },
                },
            }

        def add_canvases(manifest, canvases):
            manifest.manifest["sequences"][0]["canvases"] += canvases

        def delete_canvas(manifest, canvases_to_remove):
            canvas_ids_remove = [canvas["images"][0]["resource"]["service"]["@id"] for canvas in canvases_to_remove]
            canvases = manifest.manifest["sequences"][0]["canvases"]
            manifest.manifest["sequences"][0]["canvases"] = [
                canvas for canvas in canvases if canvas["images"][0]["resource"]["service"]["@id"] not in canvas_ids_remove
            ]

        def create_image(file):
            new_image_id = uuid.uuid4()
            new_image = models.ManifestImage.objects.create(imageid=new_image_id, image=file)
            new_image.save()

            file_name = os.path.basename(new_image.image.name)
            file_url = self.iiif_proxy_uri + "iiif/2/" + file_name
            file_json_url = settings.CANTALOUPE_HTTP_ENDPOINT + "/iiif/2/" + file_name + "/info.json"
            image_json = self.fetch(file_json_url)
            return image_json, new_image_id, file_url

        def get_image_count(manifest):
            manifest = models.IIIFManifest.objects.get(url=manifest)
            return len(manifest.manifest["sequences"][0]["canvases"])

        def change_manifest_info(manifest, name, desc, attribution, logo):
            if name is not None and name != "":
                manifest.label = name
                manifest.manifest["label"] = name
            if desc is not None and desc != "":
                manifest.description = desc
                manifest.manifest["description"] = desc
            if attribution and attribution != "":
                manifest.manifest["attribution"] = attribution
            if logo and logo != "":
                manifest.manifest["logo"] = logo

        def change_manifest_metadata(manifest):  # To be fixed
            manifest.manifest["metadata"] = metadata

        def change_canvas_label(manifest, canvas_id, label):
            # canvas_id = canvas['images'][0]['resource']['service']['@id']
            canvases = manifest.manifest["sequences"][0]["canvases"]
            for canvas in canvases:
                if canvas["images"][0]["resource"]["service"]["@id"] == canvas_id:
                    canvas["label"] = label

        acceptable_types = [
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".png",
        ]

        files = request.FILES.getlist("files")
        name = request.POST.get("manifest_title")
        attribution = request.POST.get("manifest_attribution", "")
        logo = request.POST.get("manifest_logo", "")
        desc = request.POST.get("manifest_description")
        operation = request.POST.get("operation")
        manifest_url = request.POST.get("manifest")
        canvas_label = request.POST.get("canvas_label")
        canvas_id = request.POST.get("canvas_id")
        metadata = request.POST.get("metadata")
        selected_canvases = request.POST.get("selected_canvases")
        try:
            metadata = json.loads(request.POST.get('metadata'))
        except TypeError:
            metadata = []

        if not os.path.exists(settings.CANTALOUPE_DIR):
            os.mkdir(settings.CANTALOUPE_DIR)

        if operation == "create":
            canvases = []
            for f in files:
                if os.path.splitext(f.name)[1].lower() in acceptable_types:
                    try:
                        image_json, image_id, file_url = create_image(f)
                    except:
                        return
                    canvas = create_canvas(image_json, file_url, os.path.splitext(f.name)[0], image_id)
                    canvases.append(canvas)
                else:
                    logger.warn("filetype unacceptable: " + f.name)

            pres_dict = create_manifest(canvases=canvases)
            manifest = models.IIIFManifest.objects.create(label=name, description=desc, manifest=pres_dict)
            manifest_id = manifest.id
            json_url = f"/manifest/{manifest_id}"
            manifest.url = json_url
            manifest.save()
            return JSONResponse(manifest)
        else:
            manifest = models.IIIFManifest.objects.get(url=manifest_url)

        change_manifest_info(manifest, name, desc, attribution, logo)

        if canvas_label is not None:
            change_canvas_label(manifest, canvas_id, canvas_label)

        if selected_canvases is not None:
            selected_canvases_json = json.loads(selected_canvases)
            delete_canvas(manifest, selected_canvases_json)

        if len(files) > 0:
            try:
                canvases = []
                for f in files:
                    if os.path.splitext(f.name)[1].lower() in acceptable_types:
                        try:
                            image_json, image_id, file_url = create_image(f)
                        except:
                            return
                        canvas = create_canvas(image_json, file_url, os.path.splitext(f.name)[0], image_id)
                        canvases.append(canvas)
                    else:
                        logger.warn("filetype unacceptable: " + f.name)
                add_canvases(manifest, canvases)
            except:
                logger.warning("You have to select a manifest to add images")
                return None

        if metadata:
            change_manifest_metadata(manifest)

        manifest.save()
        return JSONResponse(manifest)

    def fetch(self, url):
        try:
            resp = requests.get(url)
            return resp.json()
        except:
            logger.warn("Manifest not created. Check if Cantaloupe running")
            return None

    def on_import(self, tile):
        raise NotImplementedError

    def after_function_save(self, tile, request):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError


class IIIFServerProxyView(ProxyView):
    upstream = settings.CANTALOUPE_HTTP_ENDPOINT

    def get_request_headers(self):
        headers = super(IIIFServerProxyView, self).get_request_headers()
        if settings.CANTALOUPE_HTTP_ENDPOINT is None:
            raise Http404(_("IIIF server proxy not configured"))
        return headers

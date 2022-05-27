import json
import logging
import os
import requests
import shutil
from afs.settings import CANTALOUPE_DIR, CANTALOUPE_HTTP_ENDPOINT, MEDIA_ROOT, MEDIA_URL, APP_ROOT
from arches.app.functions.base import BaseFunction
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.tile import Tile


details = {
    "name": "File to IIIF",
    "type": "node",
    "description": "copies uploaded files into a Cantaloupe host dir, creates IIIF manifest json and db record",
    "defaultconfig": {"triggering_nodegroups": []},
    "classname": "FileToIIIF",
    "component": "views/components/functions/file-to-iiif",
    "functionid": "210519e3-ee55-460a-ab6d-0b56e1b5ba3a",
}

logger = logging.getLogger(__name__)


class FileToIIIF(BaseFunction):
    def post_save(self, tile, request):

        acceptable_types = [
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".png",
        ]  # 2nd validation in case card not configured to filter image filetypes
        files = list(models.File.objects.filter(tile=tile))
        resource = Resource.objects.get(resourceinstanceid=tile.resourceinstance_id)
        name = resource.displayname
        desc = resource.displaydescription
        if not os.path.exists(CANTALOUPE_DIR):
            os.mkdir(CANTALOUPE_DIR)

        canvases = []
        if len(files) > 0:
            for f in files:
                if os.path.splitext(f.path.name)[1].lower() in acceptable_types:
                    dest = os.path.join(CANTALOUPE_DIR, os.path.basename(f.path.url))
                    file_name = os.path.basename(f.path.name)
                    file_url = CANTALOUPE_HTTP_ENDPOINT + "iiif/2/" + file_name
                    file_json = file_url + "/info.json"
                    logger.info("copying file to local dir")
                    shutil.copyfile(os.path.join(MEDIA_ROOT, f.path.name), dest)
                    image_json = self.fetch(file_json)
                    if image_json is None:
                        return
                    canvases.append(
                        {
                            "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/canvas/TBD.json",
                            "@type": "sc:Canvas",
                            "height": image_json["height"],
                            "width": image_json["width"],
                            "images": [
                                {
                                    "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/annotation/TBD.json",
                                    "@type": "oa.Annotation",
                                    "motivation": "unknown",
                                    "on": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/canvas/TBD.json",
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
                            "label": f"{name} p. {len(canvases) + 1}",
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
                    )
                else:
                    logger.warn("filetype unacceptable: " + f.path.name)
                    return

            pres_dict = {
                "@context": "http://iiif.io/api/presentation/2/context.json",
                "@type": "sc:Manifest",
                "description": desc,
                "label": name,
                "logo": "",
                "metadata": [{"label": "TBD", "value": ["Unknown"]}],
                "thumbnail": {
                    "@id": file_url + "/full/!300,300/0/default.jpg",
                    "@type": "dctypes:Image",
                    "format": "image/jpeg",
                    "label": "Main VIew (.45v)",
                },
                "sequences": [
                    {
                        "@id": CANTALOUPE_HTTP_ENDPOINT + "iiif/manifest/sequence/TBD.json",
                        "@type": "sc:Sequence",
                        "canvases": canvases,
                        "label": "Object",
                        "startCanvas": "",
                    }
                ],
            }

            manifest = models.IIIFManifest.objects.create(label=name, description=desc, manifest=pres_dict)
            manifest_id = manifest.id
            json_url = f"/manifest/{manifest_id}"
            manifest.url = json_url
            manifest.save()

            # save the url to digital resource identifier_content node
            manifest_url_nodeid = "db05c421-ca7a-11e9-bd7a-a4d18cec433a"
            manifest_url_nodegroupid = "db05b5ca-ca7a-11e9-82ca-a4d18cec433a"
            # set the identifier type node to "url" concept
            digital_resource_identifier_type_nodeid = "db05c05e-ca7a-11e9-8824-a4d18cec433a"
            url_concept_valueid = "f32d0944-4229-4792-a33c-aadc2b181dc7"
            if not Tile.objects.filter(resourceinstance=tile.resourceinstance, nodegroup_id=manifest_url_nodegroupid).exists():
                url_tile = Tile()
                url_tile.nodegroup = models.NodeGroup.objects.get(nodegroupid=manifest_url_nodegroupid)
                url_tile.resourceinstance = tile.resourceinstance
                url_tile.data = {manifest_url_nodeid: json_url, digital_resource_identifier_type_nodeid: [url_concept_valueid]}
                url_tile.save()

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

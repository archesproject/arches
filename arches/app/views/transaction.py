from arches.app.utils.decorators import user_created_transaction_match
from arches.app.utils.transaction import (
    reverse_edit_log_entries,
    delete_manifests,
    delete_workflow_histories,
)
from arches.app.utils.response import JSONResponse
from django.utils.decorators import method_decorator
from django.views.generic import View
import logging

logger = logging.getLogger(__name__)


@method_decorator(user_created_transaction_match, name="dispatch")
class ReverseTransaction(View):
    def post(self, request, transactionid=None):
        response = dict()
        success = False
        if transactionid is not None:
            response["changes"] = reverse_edit_log_entries(transactionid)
            response["changes"] += delete_manifests(transactionid)
            response["changes"] += delete_workflow_histories(transactionid)
            success = True
        response["success"] = success
        return JSONResponse(response)

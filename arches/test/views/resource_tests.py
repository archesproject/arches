def test_api_resource_report_response(self):
    """
    Ensure api_resource_report returns proper response

    """
    self.client.login(username="admin", password="admin")
    url = reverse(
        "api_resource_report", kwargs={"resourceid": self.resource_instance_id}
    )
    response = self.client.get(url)
    self.assertTrue(len(response.json()["cardwidgets"]) > 0)

# status
Status page of OpenML


Checks:

 * [MinIO](https://min.io/docs/minio/linux/operations/monitoring/healthcheck-probe.html): `curl -I https://data.openml.org/minio/health/live` returns `200 OK`.
 * [ElasticSearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-health.html#cluster-health-api-desc): `curl -X GET "https://es.openml.org/_cluster/health?wait_for_status=yellow&timeout=10s&pretty"`
 * Website: `curl -I "https://www.openml.org/"` returns `200 OK`.
 * REST API: `curl "https://www.openml.org/api/v1/json/evaluationmeasure/list"`
 * Test Server: ?

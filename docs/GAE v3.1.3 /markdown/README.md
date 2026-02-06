# Protocol Documentation
<a name="top"></a>

## Table of Contents

- [proto/graphanalyticsengine.proto](#proto_graphanalyticsengine-proto)
    - [AqlQuery](#arangodb-cloud-internal-graphanalytics-v1-AqlQuery)
    - [AqlQuery.BindVarsEntry](#arangodb-cloud-internal-graphanalytics-v1-AqlQuery-BindVarsEntry)
    - [AqlQueryGroup](#arangodb-cloud-internal-graphanalytics-v1-AqlQueryGroup)
    - [DataItem](#arangodb-cloud-internal-graphanalytics-v1-DataItem)
    - [Empty](#arangodb-cloud-internal-graphanalytics-v1-Empty)
    - [GraphAnalyticsEngineAggregateComponentsRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAggregateComponentsRequest)
    - [GraphAnalyticsEngineAttributePropagationRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAttributePropagationRequest)
    - [GraphAnalyticsEngineBetweennessCentralityRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineBetweennessCentralityRequest)
    - [GraphAnalyticsEngineDeleteGraphResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteGraphResponse)
    - [GraphAnalyticsEngineDeleteJobResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteJobResponse)
    - [GraphAnalyticsEngineErrorResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineErrorResponse)
    - [GraphAnalyticsEngineGetGraphResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGetGraphResponse)
    - [GraphAnalyticsEngineGraph](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraph)
    - [GraphAnalyticsEngineGraphId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraphId)
    - [GraphAnalyticsEngineJob](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJob)
    - [GraphAnalyticsEngineJobId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJobId)
    - [GraphAnalyticsEngineLabelPropagationRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLabelPropagationRequest)
    - [GraphAnalyticsEngineLineRankRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLineRankRequest)
    - [GraphAnalyticsEngineListGraphsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListGraphsResponse)
    - [GraphAnalyticsEngineListJobsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListJobsResponse)
    - [GraphAnalyticsEngineLoadDataAqlRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest)
    - [GraphAnalyticsEngineLoadDataAqlRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest-CustomFieldsEntry)
    - [GraphAnalyticsEngineLoadDataRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest)
    - [GraphAnalyticsEngineLoadDataRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest-CustomFieldsEntry)
    - [GraphAnalyticsEngineLoadDataResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataResponse)
    - [GraphAnalyticsEnginePageRankRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEnginePageRankRequest)
    - [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse)
    - [GraphAnalyticsEngineShutdownResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineShutdownResponse)
    - [GraphAnalyticsEngineStoreResultsRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest)
    - [GraphAnalyticsEngineStoreResultsRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-CustomFieldsEntry)
    - [GraphAnalyticsEngineStoreResultsRequest.VertexCollectionsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-VertexCollectionsEntry)
    - [GraphAnalyticsEngineStoreResultsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsResponse)
    - [GraphAnalyticsEngineWccSccRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest)
    - [GraphAnalyticsEngineWccSccRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest-CustomFieldsEntry)
  
    - [GraphAnalyticsEngineService](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineService)
  
- [Scalar Value Types](#scalar-value-types)



<a name="proto_graphanalyticsengine-proto"></a>
<p align="right"><a href="#top">Top</a></p>

## proto/graphanalyticsengine.proto
GraphAnalyticsEngineService is an API for interacting with graph analytics engines. Each engine corresponds to a deployment on AG, granting direct database access for loading graphs and storing results. A single database deployment can accommodate multiple graph analytics engines (GAEs).

Every call, which can take longer to complete, is asynchronous in the sense that it returns a job id and the result can/must be retrieved separately. Please note that these results must be deleted explicitly to free the memory used, since all results are stored in RAM.

The following trigger asynchronous operations, which might take longer to complete:
&lt;ul&gt;
 &lt;li&gt; Load a graph from the deployment via two AQL queries (one for vertices, one for edges) [POST]&lt;/li&gt;
 &lt;li&gt; Load a graph via the arangodump protocol [POST]&lt;/li&gt;
 &lt;li&gt; Various calls to start computation jobs [POST]&lt;/li&gt;
 &lt;li&gt; Write back result of computation job to deployment [POST]&lt;/li&gt;
&lt;/ul&gt;


<a name="arangodb-cloud-internal-graphanalytics-v1-AqlQuery"></a>

### AqlQuery
AQL query with bind parameters


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| query | [string](#string) |  | AQL query string |
| bind_vars | [AqlQuery.BindVarsEntry](#arangodb-cloud-internal-graphanalytics-v1-AqlQuery-BindVarsEntry) | repeated | Bind parameters as a map of parameter names to JSON values |






<a name="arangodb-cloud-internal-graphanalytics-v1-AqlQuery-BindVarsEntry"></a>

### AqlQuery.BindVarsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [google.protobuf.Value](#google-protobuf-Value) |  |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-AqlQueryGroup"></a>

### AqlQueryGroup
Group of AQL queries to be executed in parallel


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| queries | [AqlQuery](#arangodb-cloud-internal-graphanalytics-v1-AqlQuery) | repeated |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-DataItem"></a>

### DataItem
Data item specification for vertex or edge attributes


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| name | [string](#string) |  | Attribute name |
| data_type | [string](#string) |  | Data type: &#34;Bool&#34;, &#34;String&#34;, &#34;U64&#34;, &#34;I64&#34;, &#34;F64&#34;, &#34;JSON&#34; |






<a name="arangodb-cloud-internal-graphanalytics-v1-Empty"></a>

### Empty
Empty input:






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAggregateComponentsRequest"></a>

### GraphAnalyticsEngineAggregateComponentsRequest
Request arguments for GraphAnalyticsEngineRunCompAggregation:


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| job_id | [uint64](#uint64) |  | Job ID |
| aggregation_attribute | [string](#string) |  | Aggregation attribute: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAttributePropagationRequest"></a>

### GraphAnalyticsEngineAttributePropagationRequest
Request arguments for GraphAnalyticsEngineRunAttributePropagation.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID. This attribute must be given. |
| start_label_attribute | [string](#string) |  | Start label attribute, must be stored in one column of the column store of the graph. Use id of vertex if set to &#34;@id&#34;. Values can be empty or a string or a list of strings. All other values are transformed into a string. This attribute must be given. |
| synchronous | [bool](#bool) | optional | Flag to indicate whether synchronous (true) or asynchronous label propagation is used. The default is asynchronous, i.e. `false`. |
| backwards | [bool](#bool) | optional | Flag to indicate whether the propagation happens forwards (along the directed edges) or backwards (in the opposite direction). The default is forwards, i.e. `false`. |
| maximum_supersteps | [uint32](#uint32) | optional | Maximum number of steps to do, default is 64: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineBetweennessCentralityRequest"></a>

### GraphAnalyticsEngineBetweennessCentralityRequest
Request arguments for GraphAnalyticsEngineRunPageRank:


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| k | [uint64](#uint64) | optional | Number of start vertices, use 0 to start from every single vertex in the graph for a complete result. 0 is the default. |
| undirected | [bool](#bool) | optional | Flag, if edges should be used in both directions, default is false: |
| normalized | [bool](#bool) | optional | Flag, if a normalization with 1/((N-1)*(N-2)) should be applied, where N is the size of the largest orbit found. Default is false. |
| parallelism | [uint32](#uint32) | optional | Number of threads to use: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteGraphResponse"></a>

### GraphAnalyticsEngineDeleteGraphResponse
Response for a delete graph request.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | ID of graph |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteJobResponse"></a>

### GraphAnalyticsEngineDeleteJobResponse
Response for a delete job request.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [uint64](#uint64) |  | ID of job |
| error | [bool](#bool) |  | Error? |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineErrorResponse"></a>

### GraphAnalyticsEngineErrorResponse
Generic error


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGetGraphResponse"></a>

### GraphAnalyticsEngineGetGraphResponse



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |
| graph | [GraphAnalyticsEngineGraph](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraph) |  | The graph |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraph"></a>

### GraphAnalyticsEngineGraph
Description of a graph.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | ID of graph |
| number_of_vertices | [uint64](#uint64) |  | Number of vertices: |
| number_of_edges | [uint64](#uint64) |  | Number of edges: |
| memory_usage | [uint64](#uint64) |  | Memory usage: |
| memory_per_vertex | [uint64](#uint64) |  | Memory usage per vertex: |
| memory_per_edge | [uint64](#uint64) |  | Memory usage per edge: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraphId"></a>

### GraphAnalyticsEngineGraphId
ID of an engine and id of a graph


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [string](#string) |  | Graph ID (for path) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJob"></a>

### GraphAnalyticsEngineJob
Description of a job.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [uint64](#uint64) |  | ID of the current job |
| graph_id | [uint64](#uint64) |  | Graph of the current job |
| total | [uint32](#uint32) |  | Total progress. Guaranteed to be positive, but could be 1 |
| progress | [uint32](#uint32) |  | Progress (0: no progress, equal to total: ready) |
| error | [bool](#bool) |  | Error flag |
| error_code | [int32](#int32) |  | Error code |
| error_message | [string](#string) |  | Error message |
| source_job | [string](#string) |  | Optional source job |
| comp_type | [string](#string) |  | Computation type: |
| memory_usage | [uint64](#uint64) |  | Memory usage: |
| runtime_in_microseconds | [uint64](#uint64) |  | Runtime of job in microseconds |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJobId"></a>

### GraphAnalyticsEngineJobId
ID of an engine and id of a job


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [string](#string) |  | Graph ID (for path) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLabelPropagationRequest"></a>

### GraphAnalyticsEngineLabelPropagationRequest
Request arguments for GraphAnalyticsEngineRunLabelPropagation.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| start_label_attribute | [string](#string) |  | Start label attribute, must be stored in one column of the column store of the graph. Use id of vertex if set to &#34;@id&#34;. |
| synchronous | [bool](#bool) | optional | Flag to indicate whether synchronous (true) or asynchronous label propagation is used (default is false): |
| random_tiebreak | [bool](#bool) | optional | Flag indicating if ties in the label choice are broken randomly (uniform distribution) or deterministically (smallest label amongst the most frequent ones), default is false: |
| maximum_supersteps | [uint32](#uint32) | optional | Maximum number of steps to do, default is 64: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLineRankRequest"></a>

### GraphAnalyticsEngineLineRankRequest
Request arguments for GraphAnalyticsEngineRunLineRank:


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| damping_factor | [double](#double) | optional | Damping factor, default is 0.85: |
| maximum_supersteps | [uint32](#uint32) | optional | Maximal number of supersteps, default is 64: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListGraphsResponse"></a>

### GraphAnalyticsEngineListGraphsResponse
Response arguments from GraphAnalticsEngineListGraphs.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |
| graphs | [GraphAnalyticsEngineGraph](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraph) | repeated | The graphs |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListJobsResponse"></a>

### GraphAnalyticsEngineListJobsResponse
Response arguments from GraphAnalyticsEngineListJobs.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |
| jobs | [GraphAnalyticsEngineJob](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJob) | repeated | The graphs |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest"></a>

### GraphAnalyticsEngineLoadDataAqlRequest
Request arguments for GraphAnalyticsEngineLoadDataAql.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| database | [string](#string) |  | Database to get graph from |
| vertex_attributes | [DataItem](#arangodb-cloud-internal-graphanalytics-v1-DataItem) | repeated | List of vertex attributes to load with their types (optional) |
| edge_attributes | [DataItem](#arangodb-cloud-internal-graphanalytics-v1-DataItem) | repeated | List of edge attributes to load with their types (optional) |
| phases | [AqlQueryGroup](#arangodb-cloud-internal-graphanalytics-v1-AqlQueryGroup) | repeated | AQL queries organized as a list of lists Outer list: executed sequentially (phases) Inner list: queries executed in parallel Each query returns items with format: {&#34;vertices&#34;:[...], &#34;edges&#34;:[...]} |
| batch_size | [uint64](#uint64) | optional | Optional batch size |
| custom_fields | [GraphAnalyticsEngineLoadDataAqlRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest-CustomFieldsEntry) | repeated | Map of engine-type specific custom fields (dynamic for this data-load operation) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest-CustomFieldsEntry"></a>

### GraphAnalyticsEngineLoadDataAqlRequest.CustomFieldsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest"></a>

### GraphAnalyticsEngineLoadDataRequest
Request arguments for GraphAnalyticsEngineLoadData.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| database | [string](#string) |  | Retrieve graph from the specified database |
| graph_name | [string](#string) | optional | Graph name, this is optional, because one can also use a list of vertex and edge collections: |
| vertex_collections | [string](#string) | repeated | Optional list of vertex collections. Must be set, if the `graph_name` is not given, or if data other than the graph topology is to be loaded. |
| vertex_attributes | [string](#string) | repeated | List of attributes to load into the column store for vertices. The column store of the graph will contain one column for each attribute listed here. |
| vertex_attribute_types | [string](#string) | repeated | Types for the vertex attributes. These values are allowed: - &#34;string&#34; - &#34;float&#34; - &#34;integer&#34; - &#34;unsigned&#34; |
| edge_collections | [string](#string) | repeated | List of edge collections. Must be set, if `graph_name` is not given. |
| parallelism | [uint32](#uint32) | optional | Optional numeric value for thread parallelism. This is currently used in four places. One is the number of async jobs launched to get data, another is the number of threads to be launched to synchronously work on incoming data. The third is the number of threads used on each DBServer to produce data. And the fourth is the length of the prefetch queue on DBServers. Potentially, we want to allow more arguments to be able to fine tune this better. |
| batch_size | [uint64](#uint64) | optional | Optional batch size |
| custom_fields | [GraphAnalyticsEngineLoadDataRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest-CustomFieldsEntry) | repeated | Map of engine-type specific custom fields (dynamic for this data-load operation) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest-CustomFieldsEntry"></a>

### GraphAnalyticsEngineLoadDataRequest.CustomFieldsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataResponse"></a>

### GraphAnalyticsEngineLoadDataResponse
Response arguments from GraphAnalyticsEngineLoadData.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [uint64](#uint64) |  | ID of the load data operation |
| graph_id | [uint64](#uint64) |  | Graph ID |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEnginePageRankRequest"></a>

### GraphAnalyticsEnginePageRankRequest
Request arguments for GraphAnalyticsEngineRunPageRank:


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| damping_factor | [double](#double) | optional | Damping factor, default is 0.85: |
| maximum_supersteps | [uint32](#uint32) | optional | Maximal number of supersteps, default is 64: |
| seeding_attribute | [string](#string) | optional | optional seeding attribute for a seeded pagerank, default is empty for none: |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse"></a>

### GraphAnalyticsEngineProcessResponse
Response arguments from GraphAnalyticsEngineProcess.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [uint64](#uint64) |  | ID of the job |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineShutdownResponse"></a>

### GraphAnalyticsEngineShutdownResponse
Response for a shutdown request.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| error | [bool](#bool) |  | Error? |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest"></a>

### GraphAnalyticsEngineStoreResultsRequest
Request arguments for GraphAnalyticsEngineStoreResults.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_ids | [uint64](#uint64) | repeated | ID of the jobs of which results are written |
| attribute_names | [string](#string) | repeated | Attribute names to write results to |
| database | [string](#string) |  | Database in ArangoDB to use: |
| vertex_collections | [GraphAnalyticsEngineStoreResultsRequest.VertexCollectionsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-VertexCollectionsEntry) | repeated | The following map maps collection names as found in the _id entries of vertices to the collections into which the result data should be written. The list of fields is the attributes into which the result is written. An insert operation with overwritemode &#34;update&#34; is used. |
| parallelism | [uint32](#uint32) | optional | Optional numeric value for thread parallelism |
| batch_size | [uint64](#uint64) | optional | Optional batch size |
| target_collection | [string](#string) |  | Target collection for non-graph results: |
| custom_fields | [GraphAnalyticsEngineStoreResultsRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-CustomFieldsEntry) | repeated | Map of engine-type specific custom fields (dynamic for this store-results operation) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-CustomFieldsEntry"></a>

### GraphAnalyticsEngineStoreResultsRequest.CustomFieldsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest-VertexCollectionsEntry"></a>

### GraphAnalyticsEngineStoreResultsRequest.VertexCollectionsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsResponse"></a>

### GraphAnalyticsEngineStoreResultsResponse
Response arguments from GraphAnalyticsEngineStoreResults.


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| job_id | [uint64](#uint64) |  | ID of the store results operation |
| error_code | [int32](#int32) |  | Error code, 0 if no error |
| error_message | [string](#string) |  | Error message, empty if no error |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest"></a>

### GraphAnalyticsEngineWccSccRequest
Request arguments for WCC or SCC:


| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| graph_id | [uint64](#uint64) |  | Graph ID |
| custom_fields | [GraphAnalyticsEngineWccSccRequest.CustomFieldsEntry](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest-CustomFieldsEntry) | repeated | Map of engine-type and algorithm-type specific custom fields (dynamic for this process operation) |






<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest-CustomFieldsEntry"></a>

### GraphAnalyticsEngineWccSccRequest.CustomFieldsEntry



| Field | Type | Label | Description |
| ----- | ---- | ----- | ----------- |
| key | [string](#string) |  |  |
| value | [string](#string) |  |  |





 

 

 


<a name="arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineService"></a>

### GraphAnalyticsEngineService


| Method Name | Request Type | Response Type | Description |
| ----------- | ------------ | ------------- | ------------|
| GraphAnalyticsEngineLoadData | [GraphAnalyticsEngineLoadDataRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataRequest) | [GraphAnalyticsEngineLoadDataResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataResponse) | This API call fetches data from the deployment and loads it into memory of the engine for later processing. One can either use a named graph or a list of vertex collections and a list of edge collections. Currently, the API call always loads all vertices and edges from these collections. However, it is possible to select which attribute data is loaded alongside the vertices and the edge topology. These attribute values are stored into a column store, in which each column corresponds to an attribute and has as many rows as there are vertices in the graph. Each loaded graph will get a numerical ID, with which it can be used in computations. This is an asynchronous job which returns the job id immediately. Use the GET graph API with the returned graph ID to get information on errors and the outcome of the loading. |
| GraphAnalyticsEngineLoadDataAql | [GraphAnalyticsEngineLoadDataAqlRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataAqlRequest) | [GraphAnalyticsEngineLoadDataResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLoadDataResponse) | This API fetches data from the ArangoGraph deployment via AQL and loads it into memory of the engine for later processing. AQL-based graph loading provides a flexible way to load subgraphs from ArangoDB using custom AQL queries. This approach is particularly well-suited for: &lt;ul&gt; &lt;li&gt;Loading relatively small subgraphs&lt;/li&gt; &lt;li&gt;Using indexes or traversals to find the right subgraph&lt;/li&gt; &lt;li&gt;Applying complex filtering conditions to vertices and edges&lt;/li&gt; &lt;li&gt;Executing graph traversals to define the subgraph&lt;/li&gt; &lt;/ul&gt;

&lt;p&gt;Graph Loading Specification&lt;/p&gt;

&lt;p&gt;A &#34;graph loading specification&#34; is essentially list (&#34;phases&#34;) of lists (&#34;queries&#34;) of AQL queries, where each query is a pair of a query string and a map of bind parameters. The specification has the following semantics:&lt;/p&gt;

&lt;ul&gt; &lt;li&gt;The **outer list** is executed **sequentially**&lt;/li&gt; &lt;li&gt;Each **inner list** contains queries that can be executed **in parallel**&lt;/li&gt; &lt;li&gt;Each query must return items in the following format:&lt;/li&gt; &lt;/ul&gt;

&lt;pre&gt; {&#34;vertices&#34;:[...], &#34;edges&#34;:[...]} &lt;/pre&gt;

&lt;p&gt;Both `vertices` and `edges` attributes are optional. &lt;ul&gt; &lt;li&gt;Vertex entries must contain at least an `_id` attribute&lt;/li&gt; &lt;li&gt;Edge entries must contain at least `_from` and `_to` attributes&lt;/li&gt; &lt;li&gt;Edge values can be `null` and will be silently ignored (useful for traversal start nodes)&lt;/li&gt; &lt;/p&gt;

&lt;p&gt;Furthermore, one can specify a list of attributes for vertices (&#34;vertex_attributes&#34;) and edges (&#34;edge_attributes&#34;)to be loaded. For this list, one has to give the name as well as the type of the attribute. If the query does not return the right type, a default value will be used, so that the graph analytics engine can handle the data in a type-safe manner. &lt;/p&gt; |
| GraphAnalyticsEngineRunWcc | [GraphAnalyticsEngineWccSccRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the weakly connected components algorithm (WCC) and store the results in-memory. This essentially means that the direction of edges is ignored and then the connected components of the undirected graph are computed. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunScc | [GraphAnalyticsEngineWccSccRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineWccSccRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the strongly connected components algorithm (SCC) and store the results in-memory. This means that the direction of the edges is taken into account and two vertices A and B will be in the same strongly connected component if and only if there is a directed path from A to B and from B to A. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunCompAggregation | [GraphAnalyticsEngineAggregateComponentsRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAggregateComponentsRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph and a computation which has computed connected components (weakly or strongly) by aggregating some vertex data over each component found. The result will be one distribution map for each connected component. It is stored in memory. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunPageRank | [GraphAnalyticsEnginePageRankRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEnginePageRankRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the pagerank algorithm and store the results in-memory. There are some parameters controlling the computation like the damping factor and the maximal number of supersteps. See the input message documentation for details. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunIRank | [GraphAnalyticsEnginePageRankRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEnginePageRankRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the irank algorithm and store the results in-memory. The &#34;irank&#34; algorithms is a variant of pagerank, which changes the initial weight of each vertex. Rather than being 1/N where N is the number of vertices, the value is here different depending on from which vertex collection the vertex comes. If V is from vertex collection C and N is the number of vertices in C, then the initial weight of V is 1/N. As with pagerank, the total sum of ranks stays the same as an invariant of the algorithm. There are some parameters controlling the computation like the damping factor and the maximal number of supersteps. See the input message documentation for details. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunLabelPropagation | [GraphAnalyticsEngineLabelPropagationRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLabelPropagationRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the label propagation algorithm and store the results in-memory. There are some parameters controlling the computation like the name of the attribute to choose the start label from, a flag to indicate if the synchronous or the asynchronous variant is used and the maximal number of supersteps. See the input message documentation for details. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunAttributePropagation | [GraphAnalyticsEngineAttributePropagationRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineAttributePropagationRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the attribute propagation algorithm and store the results in-memory. The algorithm basically reads a list of labels from a column for each vertex (see the loaddata operation, for which one can configure which attributes are loaded into the column store). The value can be empty or a string or a list of strings and the set of labels for each vertex is initialized accordingly. The algorithm will then simply propagate each label in each label set along the edges to all reachable vertices and thus compute a new set of labels. After a specified maximal number of steps or if no label set changes any more the algorithm stops.

BEWARE: If there are many labels in the system and the graph is well-connected then the result can be huge!

There are some parameters controlling the computation like the name of the attribute to choose the start label from, whether the synchronous or the asynchronous variant is to be used, if we propagate along the the edges forwards or backwards and the maximal number of supersteps. See the input message documentation for details. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunBetweennessCentrality | [GraphAnalyticsEngineBetweennessCentralityRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineBetweennessCentralityRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the betweenness-centrality algorithm and store the results in-memory. See https://snap.stanford.edu/class/cs224w-readings/brandes01centrality.pdf for details. There are some parameters controlling the computation like the number of start vertices, the question as to whether edges should be followed in both directions, and whether or not a normalization is done. See the input message documentation for details. The computation will return a numerical job id, with which the results can later be queried or written back to the database. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the computation. |
| GraphAnalyticsEngineRunLineRank | [GraphAnalyticsEngineLineRankRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineLineRankRequest) | [GraphAnalyticsEngineProcessResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineProcessResponse) | Process a previously loaded graph with the linerank algorithm and store the results in-memory. The algorithm measures the importance of a vertex by aggregating the importance of its incident edges. This represents the amount of information that flows through the vertex, therefore the result of this algorithm can be taken as an approximation for betweenness centrality, which is much more computation-intensive. The edge importance is computed by the probability that a random walker, visiting edges via vertices with random restarts, will stay at the edge. |
| GraphAnalyticsEngineStoreResults | [GraphAnalyticsEngineStoreResultsRequest](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsRequest) | [GraphAnalyticsEngineStoreResultsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineStoreResultsResponse) | Stores the results from previous jobs into the deployment. One can specify a number of job ids but the requirement is that they produce the same number of results. For example, results from different algorithms which produce one result per vertex can be written to the database together. The target collection must already exist and must be writable. The job produces one document per result and one can prescribe which attribute names should be used for which result. There are some parameters controlling the computation. See the input message description for details. The computation will return a numerical job id, with which the progress can be monitored. This is an asynchronous job which returns the job id immediately. Use the GET job API with the job id to get information on progress, errors and the outcome of the job. |
| GraphAnalyticsEngineListGraphs | [Empty](#arangodb-cloud-internal-graphanalytics-v1-Empty) | [GraphAnalyticsEngineListGraphsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListGraphsResponse) | List the graphs in the engine. |
| GraphAnalyticsEngineGetGraph | [GraphAnalyticsEngineGraphId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraphId) | [GraphAnalyticsEngineGetGraphResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGetGraphResponse) | Get information about a specific graph. |
| GraphAnalyticsEngineDeleteGraph | [GraphAnalyticsEngineGraphId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineGraphId) | [GraphAnalyticsEngineDeleteGraphResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteGraphResponse) | Delete a specific graph from memory. |
| GraphAnalyticsEngineListJobs | [Empty](#arangodb-cloud-internal-graphanalytics-v1-Empty) | [GraphAnalyticsEngineListJobsResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineListJobsResponse) | List the jobs in the engine (loading, computing or storing). |
| GraphAnalyticsEngineGetJob | [GraphAnalyticsEngineJobId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJobId) | [GraphAnalyticsEngineJob](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJob) | Get information about a specific job (in particular progress and result when done). |
| GraphAnalyticsEngineDeleteJob | [GraphAnalyticsEngineJobId](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineJobId) | [GraphAnalyticsEngineDeleteJobResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineDeleteJobResponse) | Delete a specific job. |
| GraphAnalticsEngineShutdown | [Empty](#arangodb-cloud-internal-graphanalytics-v1-Empty) | [GraphAnalyticsEngineShutdownResponse](#arangodb-cloud-internal-graphanalytics-v1-GraphAnalyticsEngineShutdownResponse) | Shutdown service. |

 



## Scalar Value Types

| .proto Type | Notes | C++ | Java | Python | Go | C# | PHP | Ruby |
| ----------- | ----- | --- | ---- | ------ | -- | -- | --- | ---- |
| <a name="double" /> double |  | double | double | float | float64 | double | float | Float |
| <a name="float" /> float |  | float | float | float | float32 | float | float | Float |
| <a name="int32" /> int32 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint32 instead. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="int64" /> int64 | Uses variable-length encoding. Inefficient for encoding negative numbers – if your field is likely to have negative values, use sint64 instead. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="uint32" /> uint32 | Uses variable-length encoding. | uint32 | int | int/long | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="uint64" /> uint64 | Uses variable-length encoding. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum or Fixnum (as required) |
| <a name="sint32" /> sint32 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int32s. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sint64" /> sint64 | Uses variable-length encoding. Signed int value. These more efficiently encode negative numbers than regular int64s. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="fixed32" /> fixed32 | Always four bytes. More efficient than uint32 if values are often greater than 2^28. | uint32 | int | int | uint32 | uint | integer | Bignum or Fixnum (as required) |
| <a name="fixed64" /> fixed64 | Always eight bytes. More efficient than uint64 if values are often greater than 2^56. | uint64 | long | int/long | uint64 | ulong | integer/string | Bignum |
| <a name="sfixed32" /> sfixed32 | Always four bytes. | int32 | int | int | int32 | int | integer | Bignum or Fixnum (as required) |
| <a name="sfixed64" /> sfixed64 | Always eight bytes. | int64 | long | int/long | int64 | long | integer/string | Bignum |
| <a name="bool" /> bool |  | bool | boolean | boolean | bool | bool | boolean | TrueClass/FalseClass |
| <a name="string" /> string | A string must always contain UTF-8 encoded or 7-bit ASCII text. | string | String | str/unicode | string | string | string | String (UTF-8) |
| <a name="bytes" /> bytes | May contain any arbitrary sequence of bytes. | string | ByteString | str | []byte | ByteString | string | String (ASCII-8BIT) |


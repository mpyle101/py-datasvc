# py-datasvc
Restful frontend to Datahub
  
<pre>
Base URL prefix => /api/v1

GET /tags                    => all tags (paged)
GET /tags?query=blah         => tags with any value like "blah" (paged)  
GET /tags?name=blah          => tags with names like "blah" up to limit (default:10)  
GET /tags/:id                => tag with the specified id  
GET /tags/:id/datasets       => all datasets with the specified tag
  
GET /datasets                => all datasets (paged)  
GET /datasets?query=blah     => datasets with any value like "blah" (paged)  
GET /datasets?name=blah      => datasets with names like "blah" up to limit (default:10)  
GET /datasets?tags=blah      => datasets with tags like "blah" (paged)  
GET /datasets/:id            => dataset with the specified id  

GET /platforms               => all data platforms  
GET /platforms/:id           => data platform with the specified id  
GET /platforms/:id/datasets  => all datasets for the specified platform
  
POST /tags                   => create a new tag  
    { name: string, description: string }  
DELETE /tags/:id             => delete the specified tag  
  
POST /datasets/:id/tags      => add a tag to a dataset  
    { tag: string(tid) }  
DELETE /datasets/:id/tags/:tid  => remove the tag from the dataset  
</pre>
* multiple tags are specified with comma delimiters "tags=awm1,Legacy" and are OR'd
  
paged routes support: offset & limit query parameters  
* default limit is 10, default offset is 0
not-paged routes support: limit query parameter  
* default limit is 10

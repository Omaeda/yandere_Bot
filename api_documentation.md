# [Yande.re API](https://yande.re/help/api)

## Posts

### List

The base URL is /post.xml.

- **limit** How many posts you want to retrieve. There is a hard limit of 100 posts per request.
- **page** The page number.
- **tags** The tags to search for. Any tag combination that works on the web site will work here. This includes all the meta-tags.

## Tags

### List

The base URL is /tag.xml.

- **limit** How many tags to retrieve. Setting this to 0 will return every tag.
  page The page number.
- **order** Can be date, count, or name.
- **id** The id number of the tag.
- **after_id** Return all tags that have an id number greater than this.
- **name** The exact name of the tag.
- **name_pattern** Search for any tag that has this parameter in its name.

### Related

The base URL is /tag/related.xml.

- **tags** The tag names to query.
- **type** Restrict results to this tag type (can be general, artist, copyright, or character).

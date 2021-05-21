# Progettone Master in Big Data \& Social Mining

## Gather data

### Scraping
We built a scraper to parse the top 100 charts from the Fondazione Industria Musicale Italiana.
We also built functions that uses spotify to gather information about each song.

We scraped from 2006 to 2021, are found 6,784 unique songs, of which 195 cannot be found automatically on Spotify.

Some weeks could not be retrieved from the site.
Are missing the first 17 weeks from 2006, 2 weeks from 2008, 4 weeks from 2009, 8 weeks from 2010 and 3 weeks from 2011 and the last weeks from 2021 (our scraper cannot scrape the future sadly).

### Clean data
We saw that a lot of songs that the api found were wrong using difflib. Therefore, we manually found the right spotify ID and replace them

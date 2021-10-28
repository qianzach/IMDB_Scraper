# to run 
# scrapy crawl imdb_spider -o movies.csv

import scrapy

class ImdbSpider(scrapy.Spider):
    name = 'imdb_spider'
    
    start_urls = ['https://www.imdb.com/title/tt7441658/']
    
    def parse(self, response):
        """
        the first parse() function is used to navigate and find a way to get to the Cast & Crew page
        """
        
        cast_crew = response.css("li.ipc-inline-list__item a")[2].attrib["href"]
         # If the cast and crew page exists, update the url, and move to it
        if cast_crew:
            cast_crew = response.urljoin(cast_crew) # Update url
            yield scrapy.Request(cast_crew, callback = self.parse_full_credits)
            
    def parse_full_credits(self, response):
        """
        the second parse function is used within our original parse() function in the callback argument to a yielded scrapy.Request
        
        """
        paths  = [a.attrib["href"] for a in response.css("td.primary_photo a")]  #mimics process of clicking on the headshots on this page
        
        for path in paths: #iterate through the list of paths
            actor_page =  "https://www.imdb.com/" + path[1:]
            yield scrapy.Request(actor_page, callback =  self.parse_actor_page)
    

    #def parse_full_credits(self, response):
    #        """
    #        This parse method starts on the cast and crew page and yields a scrapy.Request 
    #        for every actor listed on the page. Only includes cast members.
    #        """#
    #
    #        # Iterate through table of actors
    #        for i in range(len(response.css("table.cast_list td:not([class]) a"))):
    #            cast_page = response.css("table.cast_list td:not([class]) a")[i].attrib["href"] # Get cast member id
    #            cast_page = response.url.rsplit("/", 4)[0] + cast_page # Update url for each cast member
    #            yield scrapy.Request(cast_page, callback = self.parse_actor_page) # Move to cast member page and run parse_actor_page


    def parse_actor_page(self, response):
        """
        given that we are on the actor page, we want to yield a dictionary with two key-value pairs of the form:
        
        {"actor" : actor_name, "movie_or_TV_name" : movie_or_TV_name}
        
        Note that you will need to determine both the name of the actor and the name of each movie or TV show.
        
        This method should be no more than 15 lines of code, excluding comments and docstrings.
        """
        
        #first, we want to get the name
        name = response.css("span.itemprop::text").get() #extract the text in itemprop class to get name
        #https://docs.scrapy.org/en/latest/topics/selectors.html
        
        #Based on the actual list metadata, we want to iterate through the div class "filmo-category-section"
        # we want to iterate through every single film/show the given actor has been a part of
        
        for film in response.css("div.filmo-row").css("a::text"):
            film_name = film.get()
            if ("filming" and "announced" and "post-production" not in film_name) and film_name.find("Episode") == -1 and film_name.find("Show all") == -1 :
                yield {"name": name, "film/show": film_name    }
            
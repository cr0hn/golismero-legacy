Profile = Backbone.Model.extend({
	url: "/static/test/profiles.json",
    defaults: {
        name: ''
    }
    
});

Profiles = Backbone.Collection.extend({
	url: "/static/test/profiles.json",
    model: Profile,	
	parse : function(response){
		return response;  
   }    
});
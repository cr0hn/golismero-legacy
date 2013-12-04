User = Backbone.Model.extend({
	url: "/static/test/usuarios.json",
    defaults: {
        username: '',
        name: '',
		rol:1,
		creationDate: new Date()
    }
    
});

Users = Backbone.Collection.extend({
	url: "/static/test/usuarios.json",
    model: User,	
	parse : function(response){
		return response;  
   }    
});
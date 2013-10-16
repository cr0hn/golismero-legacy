User = Backbone.Model.extend({
	url: "/test/usuarios.json",
    defaults: {
        username: '',
        name: '',
		surname:'',
		rol:1,
		creationDate: new Date()
    }
    
});

Users = Backbone.Collection.extend({
	url: "/test/usuariosBig.json",
    model: User,	
	parse : function(response){
		return response;  
   }    
});
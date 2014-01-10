Scan = Backbone.Model.extend({
	url: "/static/test/escaneos.json",
    defaults: {
        targets: [],
        name: '',
		profile: new Profile(),
		progress:'',
		status:'',
		creationDate: new Date()
    }
    
});

Scans = Backbone.Collection.extend({
	url: "/static/test/escaneos.json?prueba",
    model: Scan,
	parse : function(response){
		return response;  
   }    
});
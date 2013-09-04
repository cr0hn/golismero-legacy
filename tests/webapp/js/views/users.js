window.UsersView = Backbone.View.extend({
	tagName: 'div',
    className: '',
    initialize: function () {
        this.render();
		this.model.bind('change', this.render, this);
        this.model.bind('remove', this.remove, this);
    },

    render: function () {
		$(this.el).html(this.template({list:this.model.toJSON()}));
		$(this.el).i18n();
        return this;
    },
	
	editUser: function(id) {
		//mostramos el formulario y cargamos los datos
		$("#form-user").removeClass("hide").addClass("show");
		$("#form-user legend:first").html(i18n.t("user.form.editUser"));
		$("#form-user > .close").click(function(){$("#form-user").addClass("hide").removeClass("show");})
	},
	
	createUser: function() {
		//reseteamos el formulario
		$("#form-user").removeClass("hide").addClass("show");
		$("#form-user legend:first").html(i18n.t("user.form.createUser"));
		$("#form-user > .close").click(function(){$("#form-user").addClass("hide").removeClass("show");})
	},
	
	removeUser: function(id) {
		user = this.model.get(id);
		user.set({name:'pepe'});
	},
	
	resetForm: function(){
		
	}	
	

});


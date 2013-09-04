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
        return this;
    },
	
	editUser: function(id) {
		alert("editUser " + id);
	},
	
	createUser: function() {
		alert("new User");
	},
	
	removeUser: function(id) {
		user = this.model.get(id);
		user.set({name:'pepe'});
	}
	

});
window.ScansView = Backbone.View.extend({
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
    }	

});


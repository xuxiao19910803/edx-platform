define(["js/views/baseview"],//add add-xblock-component-button
    function (BaseView) {

        return BaseView.extend({
            tagName: "li",
            initialize: function () {
                BaseView.prototype.initialize.call(this);
                this.template = this.loadTemplate("add-xblock-component-button");
                this.$el.html(
                    this.template({
                        type: this.model.type,
                        templates: this.model.templates,
                        display_name: this.model.display_name
                    })
                );
            }
        });

    }); // end define();

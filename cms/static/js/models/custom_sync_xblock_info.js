define(["js/models/xblock_info"],
    //更新一些额外的信息和额外方法,
    function(XBlockInfo) {
        var CustomSyncXBlockInfo = XBlockInfo.extend({
            sync: function(method, model, options) {
                //update sync
                options.url = (this.urlRoots[method] || this.urlRoot) + '/' + this.get('id');
                return XBlockInfo.prototype.sync.call(this, method, model, options);
            }
        });
        return CustomSyncXBlockInfo;
    });

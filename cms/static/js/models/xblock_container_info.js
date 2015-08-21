define(["js/models/custom_sync_xblock_info"],
    function(CustomSyncXBlockInfo) {
        //add extra information about CustomSyncXBlockInfo
        var XBlockContainerInfo = CustomSyncXBlockInfo.extend({
            urlRoots: {
                'read': '/xblock/container'
            }
        });
        return XBlockContainerInfo;
    });

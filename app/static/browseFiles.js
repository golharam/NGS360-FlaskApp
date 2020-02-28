var browseFilesDialog = function (bucket, prefix) {
    // bucket
    this.bucket = bucket;
    // prefix of directory in bucket
    this.prefix = prefix;
    this.currentDirectoryPath = prefix + "/";
};

browseFilesDialog.prototype.updateDirectoryFolder = function (newDirectory) {
    directory = newDirectory;
    $("#directorylist").empty();
    this.populateDirectoryList(directory);
};

browseFilesDialog.prototype.populateDirectoryList = function (directory) {
    var folders = directory.folders;
    var files = directory.files;
    var bucket = this.bucket;
    var currentDirectoryPath = this.currentDirectoryPath;
    var prefix = this.prefix;
    var self = this;
    if (this.currentDirectoryPath != (this.prefix + "/")) {
         $("#directorylist").append('<tr><td class="text-xs-left">' +
             '<a href="#" id="folderlevelup">' +
               '<span class="glyphicon glyphicon-level-up" aria-hidden="true"></span>&nbsp;Up a level' +
             '</a></td>' +
             '<td class="text-xs-right"></td>' +
             '<td class="text-xs-right"></td></tr>');

        $("#folderlevelup").click(function(){
            var tmpParentDirectoryPath = currentDirectoryPath.split("/");
            tmpParentDirectoryPath = tmpParentDirectoryPath.slice(0, tmpParentDirectoryPath.length-2);
            tmpParentDirectoryPath = tmpParentDirectoryPath.join("/") + "/";
            $.get("/api/v0/files?bucket="+bucket+"&prefix="+tmpParentDirectoryPath, function (data) {
                self.currentDirectoryPath = tmpParentDirectoryPath;
                self.updateDirectoryFolder(data);
            });
        });
    };
    $.each(folders, function(idx, elem){
         var anchorId = "navFolder" + idx;
         var stripped_name = elem.name.replace(currentDirectoryPath, "");
         $("#directorylist").append('<tr><td class="text-xs-left" data-sort-value="elem.name | lower">' +
             '<i class="fa fa-fw fa-folder " aria-hidden="true"></i>&nbsp;' +
             '<a href="#" id="'+anchorId+'"><strong>'+stripped_name+'</strong></a></td>' +
             '<td class="text-xs-right" data-sort-value="-1">&mdash;</td>' +
             '<td class="text-xs-right" data-sort-value="elem.date" title="elem.date">'+elem.date+'</td></tr>');
         $("#"+anchorId).click(function(){
             $.get("/api/v0/files?bucket="+bucket+"&prefix="+elem.name, function (data) {
                 directory = data;
                 self.currentDirectoryPath = elem.name;
                 self.updateDirectoryFolder(data);
             });
         });
    });
    $.each(files, function(idx, elem){
         $("#directorylist").append('<tr><td class="text-xs-left" data-sort-value="file-entry.name | lower">' +
             '<i class="fa fa-fw elem.name" aria-hidden="true"></i>&nbsp;' +
             '<a>'+elem.name+'</a></td>' +
             '<td class="text-xs-right" data-sort-value="elem.size" title="elem.size bytes">'+elem.size+'</td>' +
             '<td class="text-xs-right" data-sort-value="elem.date" title="elem.date">'+elem.date+'</td></tr>');
    });
};

browseFilesDialog.prototype.show = function () {
    url = "/api/v0/files?bucket="+this.bucket+"&prefix="+this.prefix+"/";
    var self = this;
    $("#directorylist").empty();
    $.get(url, function (data) {
        self.populateDirectoryList(data);
    });
    $('#myModalLabel').text("Files for " + this.bucket + "/" + this.prefix + "/");
    $('#fileBrowserModal').modal();
};

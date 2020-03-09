var browseFilesDialog = function (bucket, prefix) {
    // bucket
    this.bucket = bucket;
    // prefix of directory in bucket
    this.prefix = prefix;
    this.currentDirectoryPath = prefix + "/";
};

browseFilesDialog.prototype.populateDirectoryList = function () {
    var bucket = this.bucket;
    var prefix = this.prefix;
    var self = this;

    var directoryTable = $('#directorytable').DataTable({
        ajax: {
            url: "/api/v0/files?bucket="+bucket+"&prefix="+prefix+"/",
            dataSrc:  function (json) {
                allElements = [];
                if (self.currentDirectoryPath !== (prefix+"/")) {
                    allElements.push({name: '', type: 'navigator', size: '', date: ''});
                };
                $.each(json.folders, function(idx, elem) {
                    elem.type = 'folder';
                    elem.size = '';
                    elem.date = '';
                    allElements.push(elem);
                });
                $.each(json.files, function(idx, elem) {
                    elem.type = 'file';
                    allElements.push(elem);
                });
                return allElements;
            }
        },
        columns: [
            { data: "name", orderable: false,
              render: function ( data, type, row, meta ) {
                  var stripped_name = data.replace(self.currentDirectoryPath, "");

                  // show "Up one level", if we are in a subdirectory
                  if (row.type === 'navigator') {
                      folderLevelUp = function() {
                          var tmpParentDirectoryPath = self.currentDirectoryPath.split("/");
                          tmpParentDirectoryPath = tmpParentDirectoryPath.slice(0, tmpParentDirectoryPath.length-2);
                          tmpParentDirectoryPath = tmpParentDirectoryPath.join("/") + "/";
                          self.currentDirectoryPath = tmpParentDirectoryPath;
                          $('#myModalLabel').text("Files for " + bucket + "/" + self.currentDirectoryPath);
                          directoryTable.ajax.url("/api/v0/files?bucket="+bucket+"&prefix="+self.currentDirectoryPath).load();
                      };
                      return '<a href="#" onclick="folderLevelUp()"><span class="glyphicon glyphicon-level-up" aria-hidden="true"></span>&nbsp;Up a level</a>';
                  } else if (row.type === 'folder') {
                      navigateFolder = function (newPath) {
                          self.currentDirectoryPath = newPath;
                          $('#myModalLabel').text("Files for " + bucket + "/" + self.currentDirectoryPath);
                          directoryTable.ajax.url("/api/v0/files?bucket="+bucket+"&prefix="+newPath).load();
                      };
                      folderNameNoTrailingSlash = stripped_name.replace("/", "");
                      return '<i class="fa fa-fw fa-folder" aria-hidden="true"></i>&nbsp;<a href="#" onclick="navigateFolder(String.raw`'+data+'`)"><strong>'+folderNameNoTrailingSlash+'</strong></a>';
                  } else { // These are files
                      var url = "/api/v0/files/download?bucket="+bucket+"&key="+data;
                      return '<i class="fa fa-fw"></i>&nbsp;<a href="'+url+'">'+stripped_name+'</a>';
                  }
              }
            },
            { data: "size", "orderable": false },
            { data: "date", "orderable": false }
        ],
        order: [],
        deferRender: true,
        searching: true,
        paging: true,
    });

    $.fn.dataTable.ext.errMode = function ( settings, helpPage, message ) {console.log(message)};

};

browseFilesDialog.prototype.show = function () {
    var self = this;

    $('#fileBrowserModal').load('/static/browseFiles.html', function( response, status, xhr ) {
        $('#myModalLabel').text("Files for " + self.bucket + "/" + self.prefix + "/");
        self.populateDirectoryList();
    });
    $('#fileBrowserModal').modal();
};

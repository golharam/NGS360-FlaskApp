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
    $('#myModalLabel').text("Files for " + this.bucket + "/" + this.currentDirectoryPath);
    this.populateDirectoryList(directory);
};

browseFilesDialog.prototype.populateDirectoryList = function (directory) {
    var folders = directory.folders;
    var files = directory.files;
    var bucket = this.bucket;
    var currentDirectoryPath = this.currentDirectoryPath;
    var prefix = this.prefix;
    var self = this;

    var directoryTable = $('#directorytable').DataTable({
        ajax: {
            url: "/api/v0/files?bucket="+bucket+"&prefix="+prefix+"/",
            dataSrc:  function (json) {
                allElements = [];
                $.each(json.folders, function(idx, elem) {
                    elem.folder = true;
                    allElements.push(elem);
                });
                $.each(json.files, function(idx, elem) {
                    elem.folder = false;
                    allElements.push(elem);
                });
                return allElements;
            }
        },
        columns: [
            { data: "name", orderable: false,
              render: function ( data, type, row, meta ) {
                  var stripped_name = data.replace(currentDirectoryPath, "");
                  if (row.folder === true){
                      return '<i class="fa fa-fw fa-folder " aria-hidden="true"></i>&nbsp;<a href="#" id="'+data+'"><strong>'+stripped_name+'</strong></a>';
                  } else {
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

    //$("#refreshSampleListButton").on("click", function(){
    //    projectSampleTable.ajax.url("/api/v0/samples?project_id={{projectid}}&refresh=true").load();
    //});

    $.fn.dataTable.ext.errMode = function ( settings, helpPage, message ) {console.log(message)};

    // show "Up one level", if we are in a subdirectory
    if (this.currentDirectoryPath != (this.prefix + "/")) {
         $("#directorylist").append('<tr><td class="text-xs-left">' +
             '<a href="#" id="folderlevelup">' +
               '<span class="glyphicon glyphicon-level-up" aria-hidden="true"></span>&nbsp;Up a level' +
             '</a></td>' +
             '<td class="text-xs-right"></td>' +
             '<td class="text-xs-right"></td></tr>');

        $("#folderlevelup").click(function() {
            var tmpParentDirectoryPath = currentDirectoryPath.split("/");
            tmpParentDirectoryPath = tmpParentDirectoryPath.slice(0, tmpParentDirectoryPath.length-2);
            tmpParentDirectoryPath = tmpParentDirectoryPath.join("/") + "/";
            $.get("/api/v0/files?bucket="+bucket+"&prefix="+tmpParentDirectoryPath, function (data) {
                self.currentDirectoryPath = tmpParentDirectoryPath;
                self.updateDirectoryFolder(data);
            });
        });
    };
    // show folders
    $.each(folders, function(idx, elem) {
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
    // show files
    $.each(files, function(idx, elem) {
         var stripped_filename = elem.name.replace(currentDirectoryPath, "");
         var url = "/api/v0/files/download?bucket="+bucket+"&key="+elem.name;
         $("#directorylist").append('<tr><td class="text-xs-left" data-sort-value="file-entry.name | lower">' +
             '<i class="fa fa-fw elem.name" aria-hidden="true"></i>&nbsp;' +
             '<a href="'+url+'">'+stripped_filename+'</a></td>' +
             '<td class="text-xs-right" data-sort-value="elem.size" title="elem.size bytes">'+elem.size+'</td>' +
             '<td class="text-xs-right" data-sort-value="elem.date" title="elem.date">'+elem.date+'</td></tr>');
    });
};

browseFilesDialog.prototype.show = function () {
    url = "/api/v0/files?bucket="+this.bucket+"&prefix="+this.prefix+"/";
    var self = this;

    $('#fileBrowserModal').html(`<div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
                <h4 class="modal-title" id="myModalLabel"></h4>
              </div>
              <div class="modal-body">
                <div class="table-responsive">
                  <table id="listr-table" class="table table-hover">
                    <thead>
                      <tr>
                        <th class="text-xs-left " data-sort="string">Name</th>
                        <th class="text-xs-right " data-sort="int">Size</th>
                        <th class="text-xs-right " data-sort="int">Modified</th>
                      </tr>
                    </thead>
                    <tfoot>
                      <tr>
                        <td colspan="3"></td>
                      </tr>
                    </tfoot>
                    <tbody id="directorylist">
                    </tbody>
                  </table>
                </div>
                <div class="table-responsive">
                <table id="directorytable" class="table table-hover" width="100%">
                    <thead>
                    <tr>
                        <th class="text-xs-left">Name</th>
                        <th class="text-xs-right">Size</th>
                        <th class="text-xs-right">Modified</th>
                    </tr>
                    </thead>
                </table>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>`);

    $("#directorylist").empty();
    $.get(url, function (data) {
        self.populateDirectoryList(data);
    });
    $('#myModalLabel').text("Files for " + this.bucket + "/" + this.prefix + "/");
    $('#fileBrowserModal').modal();
};

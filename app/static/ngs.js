// Author: Ryan Golhar <ryan.golhar@bms.com>

// This allows us to get server-side variables into Javascript
function returnVar(vars) {
    return vars
}

function showJobStatusDialog(titleStr, jobName, jobId) {
    dialogClosed = false;
    // TBD: I think this is an old variable that is no longer used.
    logStreamName = null;

    var statusDialog = new BootstrapDialog({
        title: titleStr,
        closeByBackdrop: false,
        message: '[1/7] Submitting...<img src="/static/images/spinner.svg">',
        onhide: function(dialogRef) {
            dialogClosed = true;
        },
        jobName: jobName,
        jobId: jobId
    }).open();

    function doPoll() {
        if (dialogClosed == true) {
            return;
        }
        jobName = statusDialog.getData('jobName');
        if (jobName == null) {
            setTimeout(doPoll, 10000);
            return;
        }
        jobId = statusDialog.getData('jobId');
        $.get('/get_aws_job_state/'+jobName+'/'+jobId+'/10', function(response) {
            jobState = response['status']
            switch (jobState) {
                case "SUBMITTED":
                    status = '[2/7] Submitted...'; break;
                case "PENDING":
                    status = '[3/7] Pending...'; break;
                case "RUNNABLE":
                    status = '[4/7] Waiting for AWS resources to start &#40;this may take a few minutes&#41;...'; break;
                case "STARTING":
                    status = "[5/7] Starting..."; break;
                case "RUNNING":
                    status = '[6/7] Running...';
                    break;
                case "FAILED":
                    status = '[7/7] Failed.';
                    break;
                case "SUCCEEDED":
                    status = '[7/7] Succeeded.';
                    break;
                case "ERROR":
                    status = '';
                    break;
                default:
                    status = "[?/7] Stalled: " + jobState + ". Checking status...";
            }
            // Add the spinner
            if ((jobState != "FAILED") && (jobState != "SUCCEEDED") && (jobState != "ERROR")) {
                status += '<img src="/static/images/spinner.svg">'
            }
            // Show the log
            if ((jobState == "FAILED") || (jobState == "SUCCEEDED") || (jobState == "RUNNING") || (jobState == 'ERROR')) {
                status += '<p><div class="log">'+response['log']+'</div></p>';
            }
            // Display the status
            statusDialog.setMessage(status);
            if ((jobState != "FAILED") && (jobState != "SUCCEEDED") && (jobState != "ERROR")) {
                setTimeout(doPoll, 10000);
            }
        }).fail(function() {
            //alert("There was an unexpected error communicating with the web server.  Retrying in 10 seconds...")
            status = '<img src="/static/images/spinner.svg">There was an unexpected error retrieving the job status update, but your job is running.  Retrying in 10 seconds...'
            statusDialog.setMessage(status)
            setTimeout(doPoll, 10000);
        });
    }
    timer = setTimeout(doPoll, 10000);
    return statusDialog;
}

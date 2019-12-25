var tour = new Tour({
    backdrop: false,
    debug: true,
    steps: [
        {
            element: ".ngsTitle",
            title: "Welcome to NGS 360!",
            content: "Let's take a brief tour of the features available.",
            path: "/",
            placement: 'auto'
        },
        {
            element: ".ngsSearchbar",
            title: "Search Bar",
            content: "Search for a project by project id or name, which will take you directly to the project page.",
            path: "/",
            placement: "bottom"
        },
        {
            element: ".illuminaInfo",
            title: "Menu Options",
            content: "You can access the various pages from the menu.",
            path: "/",
            placement: "bottom"
        },
        {
            element: ".documentation",
            title: "Documentation",
            content: "SOPs & User's Guide can be found here.",
            path: "/",
            placement: "auto"
        },
        {
            element: ".atlwdg-RIGHT",
            title: "Bug Report",
            content: "If you encounter any bugs, please report it here.",
            path: "/",
            placement: "left",
        },
        {
            element: ".atlwdg-SUBTLE",
            title: "Provide Feedback",
            content: "If you want to provide any feedback, you can do so here.",
            path: "/",
            placement: "auto"
        },
        {
            element: ".tourIcon",
            title: "Take A Tour Anytime",
            content: "Click here to restart the tour at anytime.",
            path: "/",
            placement: "bottom"
        },
        {
            element: ".illuminaInfo",
            title: "Let's see some other pages",
            content: "Let's go to the Illumina Runs page",
            path: "/",
            placement: "auto"
        },
        {
            element: "#illuminaruns",
            title: "Illumina Runs",
            content: "All available runs are listed here. Clicking on a run will take you to the Run page.",
            placement: "auto",
            path: "/illumina_runs"
        },
        {
            orphan: true,
            title: "Illumina Run",
            content: "The Run page shows you the sample sheet associated with the run.",
            placement: "auto",
            path: "/illumina_run?runid=1"
        },
        {
            element: ".actions",
            title: "Available Actions",
            content: "From here you can download/upload the sample sheet, and demultiplex the run.",
            placement: "auto",
            path: "/illumina_run?runid=1"
        },
        {
            element: ".projectsMenu",
            title: "Menu Options",
            content: "Let's move on to the Projects page.",
            path: "/illumina_run?runid=1",
            placement: "bottom"
        },
        {
            orphan: true,
            title: "Projects",
            content: "All projects are listed here.  This is redudant to the search bar on the home page.  Searching for a project on the home page or clicking on the project here will both take you to the project page.",
            path: "/projects",
            placement: "bottom"
        },
        {
            orphan: true,
            title: "Project",
            content: "The project page shows information about the specific project.",
            path: "/projects/P-20160218-0001",
            placement: "bottom"
        },
        {
            element: ".exportTask",
            title: "SevenBridges",
            content: "You can import/export projects from SevenBridges.",
            path: "/projects/P-20160218-0001",
            placement: "bottom"
        },
        {
            element: ".xpressid",
            title: "Xpress",
            content: "This section shows the associated Xpress project, if one exists.",
            path: "/projects/P-20160218-0001",
            placement: "right"
        },
        {
            element: ".jobs",
            title: "Jobs",
            content: "The jobs page will show you a list of all your jobs, their status, and log",
            placement: "auto"
        },
        {
            orphan: true,
            title: "That's it!",
            content: "That's all there is to it.  Remember to refer to the documentation for more information about specific functionality, provide feedback (if you have any), and feel free to ask the NGS 360 team any questions.",
            path: "/",
            placement: "auto"
        }
    ],
    storage: window.localStorage,
    template: "<div class='popover tour'> " +
    "<div class='arrow'></div> " +
    "<h3 class='popover-title'></h3> " +
    "<div class='popover-content'></div> " +
    "<div class='popover-navigation'> " +
    "<button class='btn btn-default' data-role='prev'>« Prev</button> " +
    "<button class='btn btn-default' data-role='next'>Next »</button>" +
    "<button class='btn btn-default' data-role='end'>Got it</button> </div>",
});

var jobs_tour = new Tour({
    backdrop: false,
    debug: true,
    steps: [
        {
            element: ".jobs",
            title: "Jobs",
            content: "The jobs page will show you a list of all your jobs, their status, and log",
            placement: "auto"
        },
    ],
    storage: window.localStorage,
    template: "<div class='popover tour'> " +
    "<div class='arrow'></div> " +
    "<h3 class='popover-title'></h3> " +
    "<div class='popover-content'></div> " +
    "<div class='popover-navigation'> " +
    "<button class='btn btn-default' data-role='prev'>« Prev</button> " +
    "<button class='btn btn-default' data-role='next'>Next »</button>" +
    "<button class='btn btn-default' data-role='end'>Got it</button> </div>",
});

import { bootstrapApplication } from "@angular/platform-browser";
import { initialize } from "./app/app.config";
import { App } from "./app/app.component";

initialize()
    .then((appConfig) => bootstrapApplication(App, appConfig))
    .catch((err) => console.error(err));

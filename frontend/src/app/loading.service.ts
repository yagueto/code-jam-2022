import { Injectable } from "@angular/core";
import { Subject } from "rxjs";

@Injectable({providedIn: "root"})
export class LoadingService {
    loading: boolean = false;
    onLoadingChange: Subject<boolean> = new Subject();
}
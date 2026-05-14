import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {catchError, from, Observable, switchMap, throwError} from 'rxjs';
import {AuthenticationService} from '../authentication/authentication.service';
import {ApiConfigService} from '../../shared/api/api-config.service';

@Injectable({providedIn: 'root'})
export class FileDownloadService {
    http = inject(HttpClient);
    apiConfigService = inject(ApiConfigService);
    authService = inject(AuthenticationService);

    downloadFile(url: string): Observable<Blob> {

        const token = this.authService.accessToken();
        const headers = token
            ? new HttpHeaders().set('Authorization', `Bearer ${token}`)
            : new HttpHeaders();

        const makeRequest = (headers: HttpHeaders) =>
            this.http.get(this.apiConfigService.getBaseUrl() + url, {
                headers,
                responseType: 'blob'
            });

        return makeRequest(headers).pipe(
            catchError(err => {
                if (err.status === 401) {
                    // Call checkAuth and retry ONCE
                    return from(this.authService.checkAuth()).pipe(
                        switchMap(() => {
                            const newToken = this.authService.accessToken();
                            const newHeaders = newToken
                                ? new HttpHeaders().set('Authorization', `Bearer ${newToken}`)
                                : new HttpHeaders();
                            return makeRequest(newHeaders);
                        })
                    );
                }
                return throwError(() => err);
            })
        );
    }

    triggerDownload(blob: Blob, fileName: string): void {
        const objectUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = fileName;
        a.click();
        URL.revokeObjectURL(objectUrl);
    }

    downloadAndSave(url: string, fileName: string): void {
        this.downloadFile(url).subscribe(blob => {
            this.triggerDownload(blob, fileName);
        });
    }
}


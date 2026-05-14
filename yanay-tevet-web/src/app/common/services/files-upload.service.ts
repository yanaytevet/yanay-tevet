import {Injectable} from '@angular/core';

@Injectable({providedIn: 'root'})
export class FilesUploadService {

    async uploadFile<S>(acceptedTypes: string, useFiles: (files: File[]) => Promise<S>): Promise<S> {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.style.display = 'none';
        fileInput.accept = acceptedTypes;
        return new Promise<S>((resolve) => {
            document.body.appendChild(fileInput);
            fileInput.onchange = async () => {
                let res: S = null;
                const files = [...fileInput.files];
                if (files && files.length > 0) {
                    res = await useFiles(files);
                }
                document.body.removeChild(fileInput);
                resolve(res);
            }
            fileInput.click();
        });
    }
}


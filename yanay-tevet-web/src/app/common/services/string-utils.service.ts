import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StringUtilsService {
  CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

  public generateRandomString(length: number): string {
    let result = '';
    const charactersLength = this.CHARACTERS.length;
    for (let i = 0; i < length; i++) {
      result += this.CHARACTERS.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
  };

  public getRandomEnumValue(anEnum: any): string {
    const enumValues = Object.keys(anEnum);
    const randomIndex = Math.floor(Math.random() * enumValues.length);
    const randomEnumKey = enumValues[randomIndex];
    return anEnum[randomEnumKey];
  }
}

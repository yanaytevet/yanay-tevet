import {EnumDisplay} from './enum-display';
import {Option} from '../interfaces/util/option';

export class BooleanDisplay extends EnumDisplay {
  override data: Record<string, string> = {
    true: 'Yes',
    false: 'No',
  };

  public override getOptions(): Option[] {
    return [
      {display: 'Yes', value: true},
      {display: 'No', value: false},
    ];
  }
}

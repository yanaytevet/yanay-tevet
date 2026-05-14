import {EnumDisplay} from '../../common/string-display/enum-display';

export class BlockTypeDisplay extends EnumDisplay {
  override data: Record<string, string> = {
    round: 'Round',
    square: 'Square',
    triangle: 'Triangle',
  };
}

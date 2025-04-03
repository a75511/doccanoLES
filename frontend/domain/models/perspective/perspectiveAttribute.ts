export class PerspectiveAttributeItem {
  constructor(
    readonly id: number,
    readonly perspectiveId: number,
    readonly name: string,
    readonly type: string,
    readonly listOptions: PerspectiveAttributeListOptionItem[] = []
  ) {}

  static create(
    id: number,
    perspectiveId: number,
    name: string,
    type: string,
    listOptions: PerspectiveAttributeListOptionItem[] = []
  ): PerspectiveAttributeItem {
    return new PerspectiveAttributeItem(id, perspectiveId, name, type, listOptions);
  }
}

export class PerspectiveAttributeListOptionItem {
  constructor(
    readonly id: number,
    readonly attributeId: number,
    readonly value: string
  ) {}

  static create(id: number, 
    attributeId: number, 
    value: string): PerspectiveAttributeListOptionItem {
    return new PerspectiveAttributeListOptionItem(id, attributeId, value);
  }
}
export class UserItem {
  constructor(
    readonly id: number,
    readonly username: string,
    readonly isSuperuser: boolean,
    readonly isStaff: boolean,
    readonly firstName: string,
    readonly lastName: string,
    readonly email: string,
    readonly sex: string,
    readonly age: number
  ) {}
}

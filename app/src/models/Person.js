export default class PersonModel {
  constructor(id, firstName, lastName, partnerId) {
    this.id = id;
    this.firstName = firstName;
    this.lastName = lastName;
    this.name = firstName + ' ' + lastName;
    this.partnerId = partnerId;
    this.src = 'https://image.flaticon.com/icons/png/128/10/10522.png';
  }
}

export default class PersonModel {
  constructor(id, firstName, lastName, partnerId) {
    this.id = id;
    this.firstName = firstName;
    this.lastName = lastName;
    this.name = firstName + ' ' + lastName;
    this.partnerId = partnerId;
    this.avatar = 'https://image.flaticon.com/icons/png/128/10/10522.png';
    this.header =
      'https://venngage-wordpress.s3.amazonaws.com/uploads/2018/09/Colorful-Geometric-Simple-Background-Image.jpg';
  }
}

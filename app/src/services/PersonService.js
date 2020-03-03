import axios from 'axios';
import Config from '../config';
import PersonModel from '../models/Person';

const personUrl = Config.BASE_URL + 'persons';

let persons = [];

/**
 * Returns request URL with appropriate query parameters
 *
 * @param {object=} options
 * @private
 */
function generateUrl(options) {
  let url = personUrl;
  if (options) {
    Object.keys(options).forEach(key => {
      if (options[key] === '' || options[key] === null) {
        delete options[key];
        return;
      }
    });

    Object.keys(options).forEach((key, index) => {
      const value = options[key];
      if (isNaN(value)) {
        throw new Error(key + 'is not a number.');
      }

      if (value < 0) {
        throw new Error(key + 'cannot be less than 0.');
      }
      url += (index === 0 ? '?' : '&') + key + '=' + value;
    });
  }
  return url;
}

const PersonService = {
  /**
   * Appends optional query parameters to request and performs request to API
   *
   * @param {number=} options['pageIndex']
   * @param {number=} options['width']
   * @param {number=} options['height']
   * @public
   */
  getPersons: async function(options) {
    let url = null;
    try {
      url = generateUrl(options);
    } catch (error) {
      return Promise.reject(error.message);
    }

    return axios
      .get(url)
      .then(resp => {
        persons = resp.data.data.map(person => {
          const partner = person['partner'];
          const partnerId = partner !== null ? partner['id'] : null;
          return new PersonModel(person['id'], person['first_name'], person['last_name'], partnerId);
        });
        return Promise.resolve(persons);
      })
      .catch(err => {
        return Promise.reject(err);
      });
  },
};

export default PersonService;

import axios from 'axios';
import Config from '../config';
import PetModel from '../models/Pet';

const personUrl = Config.BASE_URL + 'persons/';
const petUrl = 'pets';

let pets = [];

/**
 * Returns request URL with appropriate query parameters
 *
 * @param {object=} options
 * @private
 */
function generateUrl(options) {
  let url = petUrl;
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

const PetService = {
  /**
   * Appends optional query parameters to request and performs request to API
   *
   * @param {number=} options['pageIndex']
   * @param {number=} options['width']
   * @param {number=} options['height']
   * @public
   */
  getPets: async function(person) {
    let url = null;
    try {
      url = personUrl + (person !== null ? person.id : '') + '/' + petUrl;
    } catch (error) {
      return Promise.reject(error.message);
    }

    return axios
      .get(url)
      .then(resp => {
        pets = resp.data.data.map(pet => {
          const owner = pet['owner'];
          const ownerId = owner !== null ? owner['id'] : null;
          return new PetModel(pet['id'], pet['name'], ownerId);
        });
        return Promise.resolve(pets);
      })
      .catch(err => {
        return Promise.reject(err);
      });
  },
};

export default PetService;

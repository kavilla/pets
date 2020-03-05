import React from 'react';
import { Button, FormGroup, FormControl, FormLabel } from 'react-bootstrap';
import { UserCard } from 'react-ui-cards';
import './Home.css';
import './../../App.css';
import PersonService from '../../services/PersonService';
import PetService from '../../services/PetService';

export default class Home extends React.Component {
  constructor(props) {
    super(props);

    this.queryParameters = {
      width: null,
      height: null,
      pageIndex: 0,
    };

    this.state = {
      currentPageIndex: 0,
      isLoading: true,
      persons: [],
      pets: [],
      showModal: false,
      selectedPerson: null,
    };

    PersonService.getPersons().then(persons => {
      this.setState(() => ({
        isLoading: false,
        persons: persons,
      }));
    });
  }

  handleUpdatePageIndex = value => {
    const nextPageIndex = this.queryParameters.pageIndex + value >= 0 ? this.queryParameters.pageIndex + value : 0;

    if (this.queryParameters.pageIndex === nextPageIndex) {
      return;
    }

    const lastPageIndex = this.queryParameters.pageIndex;
    this.queryParameters.pageIndex = nextPageIndex;

    this.setState(() => ({
      isLoading: true,
    }));

    PersonService.getPersons(this.queryParameters)
      .then(resp => {
        this.setState(() => ({
          persons: resp,
        }));
      })
      .catch(() => {
        this.queryParameters.pageIndex = lastPageIndex;
      })
      .finally(() => {
        this.setState(() => ({
          isLoading: false,
          currentPageIndex: this.queryParameters.pageIndex,
        }));
      });
  };

  handlePersonClick = person => {
    PetService.getPets(person).then(resp => {
      this.setState(() => ({
        showModal: true,
        selectedPerson: person,
        pets: resp,
      }));
    });
  };

  handleHideModal = () => {
    this.setState(() => ({
      showModal: false,
      selectedPerson: null,
      pets: [],
    }));
  };

  handleChange = (event, image) => {
    const targetId = event.target.id;
    if (targetId === 'isGray') {
      image.isGray = event.target.checked;
      this.setState({
        selectedImage: image,
      });
    }
  };

  handleSearchChange = event => {
    this.queryParameters[event.target.name] = event.target.value;
  };

  filterImages = () => {
    PersonService.getPersons(this.queryParameters).then(resp => {
      this.setState(() => ({
        isLoading: false,
        persons: resp,
      }));
    });
  };

  render() {
    const header = (
      <div className="filter-container">
        <input
          type="text"
          name="width"
          placeholder="Width..."
          className="form-control home-non-body-item filter-search-bar"
          onChange={this.handleSearchChange}
        />
        <input
          type="text"
          name="height"
          placeholder="Height..."
          className="form-control home-non-body-item filter-search-bar"
          onChange={this.handleSearchChange}
        />
        <Button className="form-control home-non-body-item" onClick={this.filterImages}>
          Filter
        </Button>
      </div>
    );

    const footer = (
      <div className="page-index-container">
        <Button className="form-control home-non-body-item btn-light" onClick={() => this.handleUpdatePageIndex(-1)}>
          Previous
        </Button>
        <span className="home-non-body-item page-index">{this.state.currentPageIndex + 1}</span>
        <Button className="form-control home-non-body-item" onClick={() => this.handleUpdatePageIndex(1)}>
          Next
        </Button>
      </div>
    );

    const body =
      !this.state.isLoading && this.state.persons.length > 0
        ? this.state.persons.map(person => {
            return (
              <UserCard
                float
                className="home-body-item"
                header={person.header}
                avatar={person.avatar}
                name={person.name}
                stats={[
                  {
                    name: 'id',
                    value: person.id,
                  },
                  {
                    name: 'married?',
                    value: person.partnerId !== null ? 'Yes' : 'No',
                  },
                ]}
                onClick={() => this.handlePersonClick(person)}
              />
            );
          })
        : null;

    const petsDiv =
      this.state.pets.length > 0
        ? this.state.pets.map(pet => {
            return (
              <div className="pet-container">
                <img src={pet.avatar} alt={pet.avatar} />
                <span>{pet.name}</span>
              </div>
            );
          })
        : null;

    const imageModal =
      this.state.showModal && this.state.selectedPerson !== null ? (
        <div className="app-modal-container">
          <div className="app-modal">
            <div className="app-modal-close-button-container">
              <Button className="app-modal-close-button btn-light" onClick={this.handleHideModal}>
                X
              </Button>
            </div>
            <h5 className="app-modal-item">
              {this.state.selectedPerson.firstName} {this.state.selectedPerson.lastName}
            </h5>
            <div className="app-modal-item img-container">
              <img src={this.state.selectedPerson.avatar} alt={this.state.selectedPerson.avatar} />
            </div>
            <div className="app-modal-item img-container">{petsDiv}</div>
          </div>
        </div>
      ) : null;

    return (
      <div className="home">
        <div className="home-non-body">{header}</div>
        <div className="home-body">{body}</div>
        <div className="home-non-body">{footer}</div>
        <div>{imageModal}</div>
      </div>
    );
  }
}

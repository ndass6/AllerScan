import React from 'react';
import {api} from '../utils/api';
import {View} from '../components/Components'

var ViewContainer = React.createClass({
  contextTypes: {
    router: React.PropTypes.object.isRequired
  },
  getInitialState: function () {
    return {
      text: 'Loading...'
    }
  },
  componentDidMount: function() {
    api.getData()
      .then(function (data) {
        this.setState({
          isLoading: false,
          text: data.text
        })
      }.bind(this))
  },
  render: function() {
    return (
      <View text={this.state.text}/>
    );
  }
});

export {ViewContainer};

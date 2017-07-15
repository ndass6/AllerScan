import React from 'react';
import {Link} from 'react-router';


var Main = React.createClass({
  render: function() {
    return (
      <div>
        <nav className="navbar navbar-default" role="navigation">
          <div className="container-fluid">
            <div className="navbar-header">
              <a className="navbar-brand" href="#">Name</a>
            </div>
          </div>
        </nav>
        <div className='main-container'>
          {this.props.children}
        </div>
      </div>
    )
  }
});

var Home = React.createClass({
  render: function() {
    return (
      <div className="container">
        <div className="jumbotron text-center">
          <h1>Hello there</h1>
          <Link to='/view'>
            <button className="btn btn-primary">Start</button>
          </Link>
        </div>
      </div>
    );
  }
});

function View(props) {
  return (
    <div className="container">
      <div className="jumbotron text-center">
        <h1>That's inner view</h1>
        <p>{props.text}</p>
      </div>
    </div>
  );
};

export {Main, Home, View};

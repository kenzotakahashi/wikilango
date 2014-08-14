var app = angular.module('wikilango', [
    'ngRoute',
    'ngResource',
    'ngAnimate',
    'utteranceControllers',
    'app.directives',
    // 'ui.bootstrap',
    'mgcrea.ngStrap',
    'ngCookies',
    'auth0',
]);

app.config(function ($routeProvider, authProvider, $httpProvider) {
    $routeProvider
      .when('/topics', {
        templateUrl: 'static/views/topics.html',
        controller: 'TopicsCtrl'
      })
      .when('/topics/:topicId', {
        templateUrl: 'static/views/edit.html',
        controller: 'EditCtrl',
        requiresLogin: true
      })
      .when('/chat/:topicId', {
        templateUrl: 'static/views/chat.html',
        controller: 'ChatCtrl',
        requiresLogin: true
      })
      .when('/logout',  {
        templateUrl: 'static/views/logout.html',
        controller: 'LogoutCtrl',
        requiresLogin: true
      })
      .when('/signup',   {
        templateUrl: 'static/views/login.html',
        controller: 'SignupCtrl',
      })
      .when('/login',   {
        templateUrl: 'static/views/login.html',
        controller: 'LoginCtrl',
      })
      // .when('/account', {
      //   templateUrl: 'static/views/account.html',
      //   controller: 'AccountCtrl',
      //   /* isAuthenticated will prevent user access to forbidden routes */
      //   requiresLogin: true
      // })
      .when('/account', {
        templateUrl: 'static/views/settings.html',
        controller: 'SettingsCtrl',
        /* isAuthenticated will prevent user access to forbidden routes */
        requiresLogin: true
      })
      .when('/contact', {
        templateUrl: 'static/views/contact.html',
      })
      .when('/user/:userId', {
        templateUrl: 'static/views/user.html',
        controller: 'UserCtrl'
      })     
      .when('/', {
        templateUrl: 'static/views/home.html',
        controller: 'HomeCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });

      authProvider.init({
        domain: 'wikilango.auth0.com',
        clientID: 'A6iqPklNDJWe7AKi2Wt7LuUpk1Iqjx5a',
        callbackURL: location.href,
        loginUrl: '/login'
      });

      authProvider.on('loginSuccess', function($location, $http) {
        $http.post('../api/v1.0/signup', {'username': 'User'}).success(function(data) {
          localStorage.setItem(data.user.auth, data.user.username);
        });
        $location.path('/topics');
      });

      authProvider.on('loginFailure', function($location, error) {
        console.log('Login failed')
        console.log(error);
        $location.path('/');
      });

      authProvider.on('logout', function() {
        console.log("Logged out");
      });

      authProvider.on('forbidden', function($location) {
        auth.signout(); 
        $location.path('/login');
      });

      $httpProvider.interceptors.push('authInterceptor');
})
.run(function(auth) {
  // This hooks al auth events to check everything as soon as the app starts
  auth.hookEvents();
});


/*
"http://goo.gl/2bfneP"
'http://goo.gl/p2jHO9'
'http://goo.gl/vd4AKi'
*/
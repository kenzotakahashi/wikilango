var utteranceControllers = angular.module('utteranceControllers', []);
if ('SpeechSynthesisUtterance' in window) {
  speechAI = new SpeechSynthesisUtterance();
}


utteranceControllers.controller('NavCtrl', function (auth, $scope, $http) {
	$scope.auth = auth;

	// This function gets called a lot. Might need refactoring.
	$scope.username = function(id) {
		return localStorage.getItem(id);
	};
});


utteranceControllers.controller('TopicsCtrl', function ($scope, $http) {
	$scope.form = false;
	$scope.topics;
	$scope.newTopic = "";
  $scope.languages = [
    {name:'English', code:'en-US'},
    {name:'Español', code:'es-ES'},
    {name:'Français', code:'fr-FR'},
    {name:'Italiano', code:'it-IT'},
    {name:'Deutsch', code:'de-DE'},
    {name:'中国的', code:'zh-CN'},
    {name:'日本語', code:'ja-JP'},
    {name:'한국의', code:'ko-KR'},
  ];


  $scope.language = $scope.languages[0];
  $scope.webSpeech = (('webkitSpeechRecognition' in window) ? true:false);

  $http.get('../api/v1.0/topics').success(function(data) {
    $scope.topics = data.topics;
    // console.log($scope.topics);
  });

  $scope.showForm = function() {
  	$scope.form = true;
  };

  $scope.submit = function() {
  	form = {
			"name": $scope.newTopic,
			"language": $scope.language.code
  	}

  	$http.post('../api/v1.0/topics', form).success(function(data) {
  		$scope.topics.push(data.topic);
  	});
  	$scope.newTopic = "";
  	$scope.form = false;
  };

  $scope.cancel = function() {
  	$scope.form = false;
  };
});

// node
// {
// 	'user',
// 	'username',
// }

utteranceControllers.controller('EditCtrl', function ($scope, $http, $routeParams, $location) {
	$scope.utterance;
	$scope.nodeSelected = false;
	$scope.selectedNode;	

	$scope.editUtterance;
	$scope.editNodeSelected = false;
	$scope.editSelectedNode;

	$scope.tooltipCreate = {"title": "Create"};
	$scope.tooltipEdit = {"title": "Edit"};
	$scope.tooltipDelete = {"title": "Delete"};

	$http.get('../api/v1.0/topics/' + $routeParams.topicId).success(function(data) {
		checkTree(data.tree);
		$scope.user = data.user;
	});

	// ============= Create =====================================

  $scope.showForm = function(node) {
  	// If this is called when there is no node in the tree, node will be undefined.
  	$scope.editNodeSelected = false;
  	$scope.utterance = "";
    $scope.nodeSelected = true;
    $scope.selectedNode = node;
  };

  $scope.submitPost = function() {
  	$scope.nodeSelected = false;

  	var utterance = {
  		'parent': (($scope.selectedNode) ? $scope.selectedNode._id : null),
  		'body': $scope.utterance,
  		'topic': $routeParams.topicId
  	};

  	$http.post('../api/v1.0/utterance', utterance).success(function(data) {
  		checkTree(data.tree);
  	});	
  };

  $scope.hover = function(node) {
  	return;
  };

  $scope.cancel = function() {
  	$scope.nodeSelected = false;  	
  };

  // ============ Edit =======================================

  $scope.showEditForm = function(node) {
  	$scope.nodeSelected = false;
  	$scope.editNodeSelected = true;
  	$scope.editUtterance = node.body;
  	$scope.editSelectedNode = node;
  };

  $scope.saveEdit = function() {
  	$scope.editNodeSelected = false;
  	var utterance = {
  		'body': $scope.editUtterance
  	}

  	$http.put('../api/v1.0/utterance/' + $scope.editSelectedNode._id, utterance).success(function(data) {
  		checkTree(data.tree);
  	});	
  };

  $scope.cancelEdit = function() {
  	$scope.editNodeSelected = false;
  }

  // =========== Delete ========================================

  $scope.deleteNode = function(node) {
  	$http.delete('../api/v1.0/utterance/' + node._id).success(function(data) {
  		checkTree(data.tree);
  	});	
  };

  $scope.deleteTopic = function() {
    $http.delete('../api/v1.0/topics/' + $routeParams.topicId).success(function(data) {
      $location.path('/topics');
    }); 
  }

  function checkTree(tree) {
  	if (tree === null) {
  		$scope.firstNode = true;
  		$scope.treeData = null;
  	} else {
  		$scope.firstNode = false;
  		$scope.treeData = [tree];
  	}
  }

  addExpandAllCollapseAll($scope);
});

function addExpandAllCollapseAll($scope) {
    function rec(nodes, action) {
        for (var i = 0 ; i < nodes.length ; i++) {
            action(nodes[i]);
            if (nodes[i].children) {rec(nodes[i].children, action);}
        }
    }
    $scope.collapseAll = function () {rec($scope.treeData, function (node) {node.collapsed = true;});};
    $scope.expandAll = function () {rec($scope.treeData, function (node) {node.collapsed = false;});};
}

utteranceControllers.controller('ChatCtrl', function ($scope, $http, $routeParams, $alert) {
  $scope.recognition = new webkitSpeechRecognition();
  $scope.userResponse = "";
  $scope.choices = [];
  $scope.turn = 0;
  $scope.historyList = [];
  $scope.tooltip = {"title": "Start / Stop speaking"}
  $scope.alertEnd = false;
  $scope.chatStarted = false;
  var recording = false;
  var chat_id;
  var miss = false;


	$scope.startChat = function() {
		$scope.historyList = [];
		$scope.alertEnd = false;
    $scope.chatStarted = true;

		$http.post('../api/v1.0/startchat/' + $routeParams.topicId, {'turn': $scope.turn}).success(function(data) {

			speechAI.lang = data.language;
      $scope.recognition.lang = data.language;
			$scope.choices = data.choices;
			chat_id = data.id;
			if (data.ai_response === null) {
				$scope.startRec();
			} else {
				speak(data.ai_response, true);
				$scope.historyList.push({'text': data.ai_response});
			}
		});
	};

  $scope.recognition.onresult = function(event) {
  	// $scope.mic = 'mic.png';
    if (event.results.length > 0) {
      $scope.userResponse = event.results[0][0].transcript;
      // console.log($scope.userResponse);

			$http.post('../api/v1.0/chat/' + chat_id, {'userResponse': $scope.userResponse}).success(function(data) {
				console.log("log: " + data.log);
				if (data.log === "Working") {
					$scope.choices = data.choices;
					pushPhrase(true);
					speak(data.ai_response, true);
					$scope.historyList.push({'text': data.ai_response});

				} else if (data.log === "End by AI") {
					speak(data.ai_response, false);
					pushPhrase(true);
					$scope.historyList.push({'text': data.ai_response});
					$scope.end();

				} else if (data.log === "End by User") {
					pushPhrase(true);
					$scope.end();

				} else if (data.log === "Try again") {
					pushPhrase(false);
					speak(data.ai_response, true);
				}
			});

    } else {
			// speak("Say again?", true);
			// TODO refactor later
			alert('length is 0');
    }
  };

  $scope.recognition.onstart = function(event) {
    recording = true;
    start_img.src = "static/images/mic-animate.gif"
  }  

  $scope.recognition.onend = function(event) {
    recording = false;
    start_img.src = "static/images/mic.png"
  }

  $scope.recognition.onerror = function(event) {
    recording = false;
    start_img.src = "static/images/mic.png"
  	console.log("error: " + event.error);
  	// $scope.historyList.push({'text': 'error'});
  };

  $scope.startRec = function() {
  	// $scope.mic = 'mic-animate.gif';
  	// $scope.alertError = false;
    if (recording) {
      $scope.recognition.stop();
      recording = false;
      start_img.src = "static/images/mic.png"
    } else {
      $scope.recognition.start();
      start_img.src = "static/images/mic-slash.png"
    }
  	
  };

  $scope.end = function() {
  	$scope.choices = [];
  	$scope.alertEnd = true;
  };

  function speak(text, onend) {
  	speechAI.text = text;
  	speechAI.onend = ((onend) ? function(event) { $scope.startRec(); } : function(event) {});
  	speechSynthesis.speak(speechAI);
  }

  function pushPhrase(success) {
  	if (miss === true) {
  		$scope.historyList.pop();
  	}
  	miss = ((success) ? false : true);
  	$scope.historyList.push({'text': $scope.userResponse});
  }

  // $scope.closeAlert = function() {

  // }

  // $scope.recognition.onstart = function(event) {
  // 	console.log('onstart called');
  // 	$scope.mic = 'mic-animate.gif';
  // };


});

utteranceControllers.controller('UserCtrl', function ($scope, $http, $routeParams) {
	$http.get('../api/v1.0/user/' + $routeParams.userId).success(function(data) {
		$scope.user = data;
	});
});

// utteranceControllers.controller('AccountCtrl', function (auth, $scope, $http) {
//   $scope.auth = auth;
//   // TODO: use $watch
// 	$http.post('../api/v1.0/signup', {'username': 'user'}).success(function(data) {
// 		$scope.user = data.user;
// 		localStorage.setItem(data.user.auth, data.user.username);
// 	});

// 	// var u = new SpeechSynthesisUtterance();
// 	// var voices = window.speechSynthesis.getVoices();
// 	// u.text = "";
// 	// u.lang = 'ja-JP';
// 	// u.voice = "Google UK English Female";
// 	// speechSynthesis.speak(u);

// });

utteranceControllers.controller('SettingsCtrl', function (auth, $scope, $http) {
	$scope.username;
	$scope.showAlert = false;
  // $scope.languages = [
  //   {name:'English', code:'en-US'},
  //   {name:'Español', code:'es-ES'},
  //   {name:'Français', code:'fr-FR'},
  //   {name:'Italiano', code:'it-IT'},
  //   {name:'Deutsch', code:'de-DE'}
  // ];


	$http.get('../api/v1.0/user/current').success(function(data) {
		$scope.username = data.username;
		// $scope.language = setLanguage(data.language);
	});

	$scope.save = function() {
		var info = {
			'username': $scope.username,
			// 'language': $scope.language
		};
		$http.post('../api/v1.0/settings', info).success(function(data) {
			$scope.username = data.username;
			// $scope.language = setLanguage(data.language);
      localStorage.setItem(data.auth, data.username);
			$scope.showAlert = true;
		});
	};

	// function setLanguage(language) {
	// 	for (var i in $scope.languages) {
	// 		if ($scope.languages[i].code === language.code) {
	// 			return $scope.languages[i];
	// 		}
	// 	}
	// }
});

utteranceControllers.controller('SignupCtrl', function (auth, $scope) {
  $scope.auth = auth;
  auth.signup();
});

utteranceControllers.controller('LoginCtrl', function (auth, $scope) {
  $scope.auth = auth;
  auth.signin();
});

utteranceControllers.controller('LogoutCtrl', function (auth, $location) {
  auth.signout();
  $location.path('/');
});

utteranceControllers.controller('HomeCtrl', function (auth, $scope, $location) {
  $scope.auth = auth;
});


// var ModalDemoCtrl = function ($scope, $modal, $log) {

//   $scope.items = ['item1', 'item2', 'item3'];

//   $scope.open = function (size) {

//     var modalInstance = $modal.open({
//       templateUrl: 'myModalContent.html',
//       controller: ModalInstanceCtrl,
//       size: size,
//       resolve: {
//         items: function () {
//           return $scope.items;
//         }
//       }
//     });

//     modalInstance.result.then(function (selectedItem) {
//       $scope.selected = selectedItem;
//     }, function () {
//       $log.info('Modal dismissed at: ' + new Date());
//     });
//   };
// };

// // Please note that $modalInstance represents a modal window (instance) dependency.
// // It is not the same as the $modal service used above.

// var ModalInstanceCtrl = function ($scope, $modalInstance, items) {

//   $scope.items = items;
//   $scope.selected = {
//     item: $scope.items[0]
//   };

//   $scope.ok = function () {
//     $modalInstance.close($scope.selected.item);
//   };

//   $scope.cancel = function () {
//     $modalInstance.dismiss('cancel');
//   };
// };
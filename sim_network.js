  // create an array with nodes
  var nodes = new vis.DataSet([
    // {id: 1, label: 'Node 1', fixed: false, physics: true, x: 10, y: 5,},
  ]);

  // create an array with edges
  var edges = new vis.DataSet([
    // {from: 1, to: 3, length: 300, width: 10},
  ]);

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = { 
    nodes: {
      scaling: {
        min: 0,
        max: 32
        }
    },
    edges: {
      arrows: {
        to: { enabled: true, scaleFactor: 1, type: "arrow" }
      }
    },
};
  var network = new vis.Network(container, data, options);

function doSomething() {
    rnd = Math.floor((Math.random() * 100) + 1);
    rnd2 = Math.floor((Math.random() * 100) + 1);
    node = {id: rnd, label: rnd.toString()}
    edge = {from: rnd, to: rnd2}
    // nodes.update(node);
    // edges.update(edge);

    const Http = new XMLHttpRequest();
    Http.open("GET", 'http://localhost:8000/nodes_created');
    Http.send();

    Http.onreadystatechange = function() {
      if(this.readyState==4 && this.status==200){
      var obj = JSON.parse(Http.responseText);
      // console.log(obj)
      nodes.update(obj);
      }
    }

    const Http2 = new XMLHttpRequest();
    Http2.open("GET", 'http://localhost:8000/edges_updated');
    Http2.send();

    Http2.onreadystatechange = function() {
      if(this.readyState==4 && this.status==200){
      var obj = JSON.parse(Http2.responseText);
      // console.log(obj)
      for (const [id, edge_group] of Object.entries(obj)) {
        console.log('edges', edges)
        console.log('id', id)
        edges.remove(id) // remove all edges that contain this from node
        console.log('edges', edges)
        // console.log('id peers',id, edge_group);
        edge_group.forEach((peer, index, array) => {
          edges.update(peer);
          console.log('peer: ', peer); 
            // console.log(index); // 0, 1, 2
        });
      }
      }
    }
    
}

setInterval(doSomething, 1000); // Time in milliseconds

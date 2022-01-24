
infinity = 1000000
invalid_node = -1

class Node:
    previous = invalid_node
    distfromsource = infinity
    visited = False

class Dijkstra:

    def __init__(self):
        '''initialise class'''
        self.startnode = 0
        self.endnode = 0
        self.network = []
        self.network_populated = False
        self.nodetable = []
        self.nodetable_populated = False
        self.currentnode = 0

    def populate_network(self, filename):
        '''populate network data structure'''
        self.network_populated = False
        try:
            networkfile = open("network.txt", 'r')
        except IOError:
            print("txt file does not exist!")
            return
        #load network.txt line by line and add contents to self.network
        #need to get rid of line feeds in file
        #convert strings into lists of individual int values
        for line in networkfile:
            self.network.append([int(char) for char in line.strip().split(',')])
        networkfile.close()
        self.network_populated = True
        
    def populate_node_table(self):
        '''populate node table'''
        #build up node table using Node() objects
        #every node in the network should have an entry
        #we also need to work the size of the network from the information we already have

        for line in self.network:
            #add Node to self.nodetable
            self.nodetable.append(Node())
        #initialise start node - dist from source of start node must 0
        self.nodetable[self.startnode].distfromsource = 0

    def parse_route(self, filename):
        '''load in route file'''
        route = []
        routefile = open("route.txt", 'r')
        for line in routefile: #only one line. In the case of multiple lines, only the last line is stored
            route = [ord(char)-65 for char in line.strip().split('>')] #A = 0, B= 1, etc.
        routefile.close()
        #startnode is first entry in list, endnode the second
        self.startnode = route[0]
        self.endnode = route[1]
    
    def return_near_neighbour(self):
        '''determine nearest neighbours of current node - returns list of the nodes that are neighbours of the current node'''
        n = []
        for index, dist in enumerate(self.network[self.currentnode]):
            if dist !=0 and not self.nodetable[index].visited:
                n.append(index)
        return n
    
    def calculate_tentative(self):
        '''calculate tentative distances of nearest neighbours'''
        nn = self.return_near_neighbour()
        # if not nn:
        #     print("Error!! End node does not exist/start node does not exist!!")
        #     exit()
        # else:
        for nodeindex in nn:
            tentative_dist = self.nodetable[self.currentnode].distfromsource + self.network[self.currentnode][nodeindex]
            if tentative_dist < self.nodetable[nodeindex].distfromsource:
                self.nodetable[nodeindex].distfromsource = tentative_dist
                self.nodetable[nodeindex].previous = self.currentnode
        
    def determine_next_node(self):
        self.calculate_tentative()
        t = infinity
        i=0
        for items in self.nodetable:
            if items.distfromsource<=t and items.visited != True:
                t=items.distfromsource 
                self.currentnode=i
            i+=1
        self.nodetable[self.currentnode].visited = True 

    def calculate_shortest_path(self):
        '''calculate shortest path across network'''
        
        while self.currentnode!=self.endnode:
            #self.calculate_tentative()
            self.determine_next_node()

    def return_shortest_path(self):
        '''return shortest path as list (start->end), and total distance'''
        shortestPath=[]
        k = 0
        if self.currentnode==self.endnode:
            k=self.nodetable[self.currentnode].distfromsource
            h=self.currentnode
            while h!=invalid_node:
                shortestPath.append(h)
                h=self.nodetable[h].previous
        if shortestPath:
            shortestPath.reverse()
        return shortestPath,k



class MaxFlow(Dijkstra): #inherits from Dijkstra class
    def __init__(self):
        '''initialise class'''
        Dijkstra.__init__(self)
        self.original_network = []
        #self.residual_graph = []
        self.max_flow = 0
        self.paths = []
        self.path = []
        # self.path = []
        # self.path[0]=self.startnode


    def populate_network(self, filename):
        '''Dijkstra method + need to make a copy of original network'''
        Dijkstra.populate_network(self, filename)
        #need to store copy of self.network in self.original_network
        self.original_network = self.network
        
    def determine_next_node(self):
        '''determine next node to examine, taking into account flow mechanics'''
        if self.currentnode!=invalid_node:
            n = []
            s = 0
            i=self.currentnode
            n = self.return_near_neighbour() 
            if not n:
                if not self.path:
                    self.currentnode = self.nodetable[self.currentnode].previous
                    self.determine_next_node()
                else:
                    self.path.pop()
                    self.currentnode = self.nodetable[self.currentnode].previous
                    self.determine_next_node()
            else:
                for items in n:
                    if self.network[self.currentnode][items]>s:
                        s = self.network[self.currentnode][items]
                        self.nodetable[items].previous = i
                        self.currentnode = items
                self.nodetable[self.currentnode].visited = True
                self.path.append(self.currentnode)
        else:
            print("*****************Residual graph******************")
            self.print_residual_graph()
            print("***************Max flow*******************")
            print(" Max flow is:", self.return_max_flow())

    def return_bottleneck_flow(self):
        '''determine the bottleneck flow of a given path'''
        m = infinity
        y = self.currentnode
        while y!=invalid_node:
            if self.nodetable[y].previous !=invalid_node:
                if self.original_network[y][self.nodetable[y].previous]<m:
                    m = self.original_network[y][self.nodetable[y].previous]
            y = self.nodetable[y].previous
        return m
    
    def print_residual_graph(self):
        for items in self.original_network:
            print(items)

    def remove_flow_capacity(self):
        '''remove flow from network and return both the path and the amount removed'''
        y = self.return_bottleneck_flow()
        self.max_flow+=y
        print("Bottleneck flow is:", y)
        for items in self.path:
            self.original_network[items][self.nodetable[items].previous]-=y
            self.original_network[self.nodetable[items].previous][items]-=y

             
    def return_max_flow(self):
        '''calculate max flow across network, from start to end, and return both the max flow value and all the relevant paths'''
        return self.max_flow

    # def display_path(self): 
    #     print(self.currentnode)
    #     for items in self.path:
    #         print(items)
        

    def find_path(self):
        self.path.clear()
        self.currentnode=self.startnode
        self.nodetable[self.startnode].visited=True
        while self.currentnode != self.endnode and self.currentnode!=invalid_node:
            self.determine_next_node()
        if self.currentnode==self.endnode:
            self.paths.append(self.path)
            self.remove_flow_capacity()
            self.path.insert(0,self.startnode)
            print(self.path)
            print()
        if self.path:
            self.paths.append(self.path)
        return self.path

if __name__ == '__main__':
        print('\033[33m'+"DIJSKTRA'S ALGORITHM")
        print('\033[39m')
        Algorithm = Dijkstra()
        Algorithm.populate_network("network.txt")
        Algorithm.parse_route("route.txt")
        Algorithm.populate_node_table()
        Algorithm.currentnode = Algorithm.startnode
        l=[]
        a=0
        Algorithm.calculate_shortest_path()
        l,a=Algorithm.return_shortest_path()
        print("***********The shortest path is*********")
        print(l)
        print("The distance is: ",a )
        print("*********The node table*********")
        for node in Algorithm.nodetable:
            print(node.previous, node.distfromsource, node.visited)
        print()
        print('\033[33m' + "MAX FLOW PROBLEM")
        print('\033[39m')
        maximumFlow = MaxFlow()
        maximumFlow.populate_network("network.txt")
        maximumFlow.parse_route("route.txt")
        maximumFlow.populate_node_table()
        maximumFlow.currentnode = maximumFlow.startnode
        print("************ Paths discovered *************")
        way=[]
        way=maximumFlow.find_path()
        while way:
            maximumFlow.nodetable.clear()
            #maximumFlow.currentnode==maximumFlow.startnode
            maximumFlow.populate_node_table()
            way=maximumFlow.find_path()
        # for node in Algorithm.nodetable:
        #     print(node.previous, node.distfromsource, node.visited)
        


       
    






        
import xml.etree.ElementTree as ET
from xmlobject import XMLObject

class XMLReader(XMLObject):
    """
    A class to handle reading and parsing of XML files for the simulator and 
    parameters configuration files.

    Public API:
        read(self) ------> the parsing function
    """

    _file = None
    _root = None
    
    def __init__(self, file_, template):
        """ 
        Construct a new XMLReader instance

        Scope:
            Public
        Parameters:
            file_ ------> path to the file containing the XML
            template ---> 'simulator' or 'parameters'
        Return:
            A new XMLReader instance  
        """

        super(XMLReader, self).__init__(file_, template)

        _tree = None
        try:
            _tree = ET.parse(file_)
        except IOError:
            raise Exception('[XMLReader.__init__] Could not open ' + str(file_))
        except ET.ParseError:
            raise Exception('[XMLReader.__init__] Could not parse ' + str(file_))
         
        self._root = _tree.getroot()

    def _parse_parameters(self):
        """ 
        Parse a parameters configuration file
     
        Scope:
            Private 
        Parameters:
            None
        Return:
            A dictionary encapsulating the parameters. 
        """

        result = {}
        for sub in self._root:
            sub_dict = {}
            try:
                if not sub.get('id') == None:
                    for attr in sub.items():
                        if not attr[0] == 'id': sub_dict[attr[0]] = float(attr[1])
                    result[(sub.tag, sub.get('id'))] = sub_dict
                else:
                    for attr in sub.items():
                        sub_dict[attr[0]] = float(attr[1])
                    result[sub.tag] = sub_dict
            except:
                raise Exception(
                    '[XMLReader._parse_parameters] Bad value in XML!')

        return {self._root.tag : result} 
 
    def _parse_simulation(self):
        """ 
        Parse a simulation configuration file
       
        Scope: 
            Private 
        Parameters:
            None
        Return:
            A list of the objects in the simulation. 
        """

        simulator_objects = []

        # robots
        for robot in self._root.findall('robot'):
            robot_type = robot.get('type')
            supervisor = robot.find('supervisor')
            if supervisor == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No supervisor specified!')

            pose = robot.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')

            try:
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')

                simulator_objects.append(('robot',
                                          robot_type,
                                          supervisor.attrib['type'],
                                          (float(x),
                                           float(y),
                                           float(theta))))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid robot (bad value)!') 

        # obstacles
        for obstacle in self._root.findall('obstacle'):
            pose = obstacle.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')

            geometry = obstacle.find('geometry')
            if geometry == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLReader._parse_simulation] Invalid point!')
                    points.append((float(x), float(y)))

                if len(points) < 3:
                    raise Exception(
                        '[XMLReader._parse_simulation] Too few points!')

                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')

                simulator_objects.append(('obstacle',
                                          (float(x),
                                           float(y),
                                           float(theta)),
                                          points))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid obstacle (bad value)!')
        
        # background
        for marker in self._root.findall('marker'):
            pose = marker.find('pose')
            if pose == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No pose specified!')
            
            geometry = marker.find('geometry')
            if geometry == None:
                raise Exception(
                    '[XMLReader._parse_simulation] No geometry specified!')
            try:
                points = []
                for point in geometry.findall('point'):
                    x, y = point.get('x'), point.get('y')
                    if x == None or y == None:
                        raise Exception(
                            '[XMLReader._parse_simulation] Invalid point!')
                    points.append((float(x), float(y)))
                    
                if len(points) < 3:
                    raise Exception(
                        '[XMLReader._parse_simulation] Too few points!')
                
                x, y, theta = pose.get('x'), pose.get('y'), pose.get('theta')
                if x == None or y == None or theta == None:
                    raise Exception(
                        '[XMLReader._parse_simulation] Invalid pose!')
                
                simulator_objects.append(('marker',
                                          (float(x),
                                           float(y),
                                           float(theta)),
                                          points))
            except ValueError:
                raise Exception(
                    '[XMLReader._parse_simulation] Invalid marker (bad value)!')
    
        return simulator_objects
 
    def read(self):
        """ 
        Call the correct parsing function 
       
        Scope:
            Public 
        Parameters:
            None
        Return:
            The result of reading and parsing the file (type dependent on the 
            template)
        """
 
        if self._template == "parameters":
            return self._parse_parameters()
        elif self._template == "simulation":
            return self._parse_simulation()
        else:
            raise Exception(
                '[XMLReader.read] Unknown template!')

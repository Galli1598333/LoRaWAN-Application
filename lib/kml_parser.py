import xml.etree.ElementTree as ET


class KmlParser:
    def __init__(self, merged_fpath):
        self.merged_fpath = merged_fpath

    def merge_files(self, count_fpath, track_fpath):
        with open(count_fpath, 'r') as file:
            count = file.read()

        with open(track_fpath, 'r') as file:
            track = file.read().replace("</gx:Track>", count + "</gx:Track>")

        with open(self.merged_fpath, 'w') as file:
            file.write(track)
        return

    def __parse(self, root):
        result_map = {}
        for child in root[0][1][0][-1][0][0]:
            result_map[int(child.text)] = {'when': '', 'coord': []}

        ids = list(result_map.keys())
        i = 0
        for child in root[0][1][0]:
            data = child.text.split(' ')
            if data[0] != '\n':
                if 'when' in child.tag:
                    result_map[ids[i]]['when'] = data[0]
                elif 'coord' in child.tag:
                    result_map[ids[i]]['coord'] = data
                    i = i + 1
        return result_map

    def parse_string(self, kml_track):
        root = ET.fromstring(kml_track)
        return self.__parse(root)

    def parse_merged(self):
        tree = ET.parse(self.merged_fpath)
        root = tree.getroot()
        return self.__parse(root)

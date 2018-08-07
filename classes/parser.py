
import re

# Simple csharp clsses parser
class Parser:    
    def __init__(self):
        self.regex_class_begin = r"class\s+([a-zA-Z]+)\s+{";
        self.regex_atribute = r"\[[\w|\.|(|,|\"|)|=|\s]+]";

    # Позволяет парсить классы из cs файлов
    # для общего файла фозвращяет map<file, hash>
    # для других [file, (start_pos, end_pos)]
    def parse_file(self, content, is_common_file):
        print("Log: parse {} file".format("common" if is_common_file else "class"));
        pattern_class_begin = re.compile(self.regex_class_begin);
        map_file = dict() if is_common_file else list();
        for i in range(len(content)):
            match = pattern_class_begin.search(content[i])
            if match != None:
                start = i;
                #find class end
                open_braces = 1;
                while(open_braces != 0):
                    i += 1;
                    st = content[i];
                    if st.find('{') != -1:
                        open_braces += 1;
                    if st.find('}') != -1:
                        open_braces -= 1;
                end = i;
                # add to map
                if is_common_file:
                    #print ("Class was found at {0}-{1}: name: {class_name}".format( start, end, class_name = match.groups()[0]))
                    map_file[match.groups()[0]] = hash(str(content[start : end]));
                else:
                    map_file.append( ( (match.groups()[0], hash(str(content[start : end]))) , (start, end)) );
        print("Found: {} classes".format(len(map_file)));
        return map_file;

    # return back start, end position
    def find_position_with_attribute(self, content, start, end):
##        pattern_attribute = re.compile(self.regex_atribute);
##        is_atttribute = lambda s : pattern_attribute.search(s) != None;
        is_atttribute = lambda s : s.find('[') != -1 and s.find(']') != -1;
        back_ind = start - 1;
        while( True ):
            if is_atttribute( content[back_ind] ):
                back_ind -= 1;
                continue;
            break;
        start = start if back_ind == start - 1 else back_ind + 1;
        return start, end;

import zstandard as zstd
import argparse
import json

def save_hlt_to_json(sourcepath, targetpath) :
    with open(sourcepath, 'rb') as sourcefile :
        dctx = zstd.ZstdDecompressor()
        reader = dctx.stream_reader(sourcefile)
        content = ''
        while True :
            chunk = reader.read(16384)
            if not chunk:
                break
            content += chunk.decode('utf-8')

        with open(targetpath, 'w') as targetfile :
            # write beautifully if it is a json.
            if targetpath.endswith('.json') :
                parsed = json.loads(content)
                newcontent = json.dumps(parsed, indent=4, sort_keys=True)
                targetfile.write(newcontent)
            else :
                targetfile.write(content)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='Decompress zstd to target file.')
    parser.add_argument('source', help='file to decompress')
    parser.add_argument('target', help='destination file')
    args = parser.parse_args()
    sourcepath = args.source
    targetpath = args.target
    
    save_hlt_to_json(sourcepath, targetpath)
"""
SQLITE3 database for segmentation challenge.
"""
import os
import re
import sqlite3
import subprocess

class C3dDB(object):
    """
    Do stuff.

    Attributes
    ----------
    conn, cursor : sqlite3 database objects
        Use these to talk to the database.
    data_root : str
        Full path to root directory of the storage.  Under this directory,
        there should be "data" and "results" directories.
    """
    def __init__(self, data_root):
        self.data_root = data_root

        self.conn = sqlite3.connect('c3d.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.conn.close()

    def run(self):
        """
        Do everything.
        """
        self.create_tables()

    def create_collections(self):
        """Create (and populate) the collections table."""
        self.cursor.execute("""DROP TABLE IF EXISTS collections;""")
        self.cursor.execute("""CREATE TABLE collections
                               (id INTEGER PRIMARY KEY,
                                name text);""")

        for collection in ['cumc', 'lidc', 'moffitt', 'rider', 'stanford']:
            sql = """INSERT INTO collections(name) VALUES ("{0}");"""
            command = sql.format(collection)
            self.cursor.execute(command)


    def create_users(self):
        """Create (and populate) the users table."""
        self.cursor.execute("""DROP TABLE IF EXISTS users;""")
        self.cursor.execute("""CREATE TABLE users
                               (id INTEGER PRIMARY KEY,
                                name text);""")

        for collection in ['cumc', 'moffitt', 'stanford']:
            sql = """INSERT INTO users(name) VALUES ("{0}");"""
            command = sql.format(collection)
            self.cursor.execute(command)


    def create_runs(self):
        """
        Create the runs.

        Schema
        ------
        id : basic row number
        base_image : identifies the image.  Not a filename but rather a label.
        label : str
            Perhaps there are more than one set of objects being 
            segmented per image?  Look at cumc/cumc/lesions[1-12]
        use_id : same id number as primary key in the users table
        repetition_num : will be 1, 2, or 3
        filename :  filename as known NOW
        original_name : original name when files first accessed
        """
        self.cursor.execute("""DROP TABLE IF EXISTS runs;""")
        self.cursor.execute("""CREATE TABLE runs
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                base_image_id INTEGER,
                                label TEXT,
                                user_id INTEGER,
                                repetition_num INTEGER,
                                name TEXT,
                                original_name TEXT,
                                FOREIGN KEY(base_image_id) REFERENCES base_images(id),
                                FOREIGN KEY(user_id) REFERENCES users(id));""")

        # Rather than walk the directories, use the information in the 
        # users table to infer what the directory paths will be.
        self.cursor.execute("""SELECT * from users;""")
        for user_id, username in self.cursor.fetchall():
            # Go thru each user.  We now have the user_id field.
            self.cursor.execute("""SELECT * from collections;""")
            for collection_id, collection in self.cursor.fetchall():

                # We now have the needed collection_id field.

                # We need all the information for this particular collection.
                sql = """SELECT id, name from base_images WHERE collection_id = {0}"""
                sql = sql.format(collection_id)
                self.cursor.execute(sql)
                collection_results = self.cursor.fetchall()

                # Go thru the collections for each user.
                full_root = os.path.join(self.data_root, 'results', username, collection)
                for root, dirs, _ in os.walk(full_root):
                    print("root={0}".format(root))
                    # Each subdirectory here is a label for the base image.
                    for label in dirs:

                        print("label={0}".format(label))
                        # An "orig" directory is never one for us to considr as a label.
                        if label == "orig" or label == 'Edited':
                            print('skipping orig directory...')
                            continue

                        # We now have the label field.
                        for _root, _dirs, files in os.walk(os.path.join(root, label)):

                            print("_root is {0}".format(_root))
                            # Some directories are empty.  Skip them
                            if len(files) == 0:
                                print('skipping empty directory...')
                                continue
                            if _root.endswith('Edited'):
                                print('skipping bogus directory...')
                                continue

                            #if username == 'stanford' and collection == 'stanford':
                            #    import pdb; pdb.set_trace()
                            base_id = determine_base_id_from_results(files, collection_results)

                            # Each file is possibly an entry into the runs table.
                            for filename in files:
                                if bogus_file(filename):
                                    continue

                                # if the filename is the same as that reference in the base
                                # image table, skip that as well.
                                sql = """SELECT name from base_images where id = {0};"""
                                sql = sql.format(base_id)
                                self.cursor.execute(sql)
                                base_results = self.cursor.fetchone()
                                if base_results[0].endswith(filename):
                                    print('skipping base image in results directory...')
                                    continue
                                if (base_results[0] + '.gz').endswith(filename):
                                    print('skipping base image in results directory...')
                                    continue

                                repetition_number = self.determine_repetition_number(filename)

                                sql = """INSERT INTO runs(base_image_id, label, user_id, repetition_num, name, original_name)
                                         VALUES ({base_image_id}, "{label}", {user_id}, {repnum}, "{name}", "{orig_name}")"""
                                command = sql.format(base_image_id=base_id, 
                                                     label=label, 
                                                     user_id=user_id,
                                                     repnum=repetition_number,
                                                     name=os.path.join(root, label, filename),
                                                     orig_name=os.path.join(root, label, filename))
                                self.cursor.execute(command)


        # Go thru the results folder.
        for user in ['cumc', 'moffitt', 'stanford']:
            root = os.path.join(self.data_root, user)
            print(root)


    def determine_repetition_number(self, filename):
        """
        There should be a regular expression pattern of either [-_][23][-_]
        if the repetition number is 2 or 3.  If not, we default to one.
        """
        regex = re.compile(r"""[-_](?P<repnum>[23])[-_]""")
        match = regex.search(filename)
        if match is None:
            return 1
            import pdb; pdb.set_trace()
        else:
            return int(match.group('repnum'))

    def create_base_images(self):
        """
        Create the base_image table.
        """
        self.cursor.execute("""DROP TABLE IF EXISTS base_images;""")
        self.cursor.execute("""CREATE TABLE base_images
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                collection_id INTEGER,
                                name TEXT,
                                original_name TEXT,
                                FOREIGN KEY(collection_id) REFERENCES collection(id));
                                """)

        # Rather than walk the directories, use the information in the 
        # collections table to infer what the directory paths will be.
        self.cursor.execute("""SELECT * from collections;""")
        for row in self.cursor.fetchall():
            collection_id, collection_name = row
            full_root = os.path.join(self.data_root, 'data', collection_name)
            for root, _, files in os.walk(full_root):
                for filename in files:
                    if filename.startswith(".") or filename.endswith(".gz"):
                        # Don't bother with .DS_Store files.
                        # It would seem that all the .nii files have duplicates
                        # as *.nii.gz.  Just ignore those as well.
                        continue

                    sql = """INSERT INTO base_images(collection_id, name, original_name)
                             VALUES ({0}, "{1}", "{2}");"""
                    command = sql.format(collection_id,
                                         os.path.join(root, filename),
                                         os.path.join(root, filename))
                    self.cursor.execute(command)


    def create_dice(self):
        """
        Create the table for the dice similarity coefficient.
        """
        regex = re.compile("Dice similarity coefficient:\s*(?P<dice>(-{0,1}nan|\d(.\d*){0,1}))");

        self.cursor.execute("""DROP TABLE IF EXISTS dice;""")
        self.cursor.execute("""CREATE TABLE dice
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                base_image_id INTEGER,
                                run_id_1 INTEGER,
                                run_id_2 INTEGER,
                                dice_similiarity_coefficient REAL,
                                FOREIGN KEY(run_id_1) REFERENCES run(id),
                                FOREIGN KEY(run_id_2) REFERENCES run(id),
                                FOREIGN KEY(base_image_id) REFERENCES base_images(id));""")

        # Now go thru all the base images.  For each one, compute the dice
        # similarity coefficient for all the associated runs.
        self.cursor.execute("""SELECT id, collection_id, name from base_images;""")
        results = self.cursor.fetchall()
        for base_image_id, collection_id, name in results:
            sql = """SELECT id, label, name from runs where base_image_id = {0};"""
            sql = sql.format(base_image_id)
            self.cursor.execute(sql)
            inter_results = self.cursor.fetchall()

            # For each run, find all the other runs with the same label.
            for run_id_1, label_1, run_file_1 in inter_results:
                # Now select all the other runs that have the same label.
                sql = 'SELECT id, label, name FROM runs WHERE base_image_id = {0} '
                sql += 'AND label="{1}"'
                sql = sql.format(base_image_id, label_1)
                self.cursor.execute(sql)
                intra_label_results = self.cursor.fetchall()

                for run_id_2, label_2, run_file_2 in intra_label_results:
                    # Run c3d on these two files, parse out the results.
                    command = 'c3d -verbose {0} {1} -overlap 1'
                    command = command.format(str(run_file_1), str(run_file_2))
                    print(command)
                    try:
                        output = subprocess.check_output(command.split(' '))
                        
                        match = regex.search(output)
                        if match is None:
                            raise RuntimeError("Could not parse c3d output.")
                        elif match.group('dice') == 'nan' or match.group('dice') == '-nan':
                            dice = 'NULL'
                        else:
                            dice = match.group('dice')
                    except subprocess.CalledProcessError:
                        # Because a file is corrupt?
                        dice = 'NULL'

                    sql = """INSERT INTO dice(base_image_id, run_id_1, run_id_2, dice_similiarity_coefficient)
                             VALUES ({0}, {1}, {2}, {3});"""
                    command = sql.format(base_image_id,
                                         run_id_1,
                                         run_id_2,
                                         dice)
                    self.cursor.execute(command)



    def create_tables(self):
        """
        Create the following tables.

        1) runs
        2) volumes
        3) dice
        4) collection
        5) base_image
        6) users
        """
        self.create_collections()
        self.create_users()
        self.create_base_images()
        self.create_runs()
        self.create_dice()

        self.cursor.execute("""DROP TABLE IF EXISTS volumes;""")
        self.cursor.execute("""CREATE TABLE volumes
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                run_id INTEGER,
                                volume REAL,
                                integral REAL);""")

        tablenames = ['runs', 'volumes', 'dice', 'collections', 'base_image',
                      'users']
        for table in tablenames:
            sql = """SELECT sql from sqlite_master WHERE name = '{0}';"""
            command = sql.format(table)
            print(command)
            for row in self.cursor.execute(command):
                print(row[0])


def bogus_file(filename):
    if filename == ".DS_Store" or filename == "Icon":
        # These are bogus, ignore them.
        return True
    if filename.endswith(".png") or filename.endswith(".dcm"):
        # Don't bother with PNGs!!!  Or DICOMs!!!
        return True
    return False


def determine_base_id_from_results(results_files, collection_results):
    """Before anything else, determine which base image
    we are dealing with.  One of these files should
    have the same name as a base image.
    """
    base_id = None
    for filename in results_files:
        if bogus_file(filename):
            continue

        for prospective_id, name in collection_results:
            if name.endswith(filename):
                base_id = prospective_id
    if base_id is None:
        import pdb; pdb.set_trace()
        raise RuntimeError("Did not determine the base image id.")

    return base_id

if __name__ == "__main__":
    DATA_ROOT = '/autofs/space/getafix_001/users/jevans/ctSeg'
    OBJ = C3dDB(DATA_ROOT)
    OBJ.run()


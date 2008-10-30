"""Module for testing cursor variables."""

import struct
import sys

class TestCursorVar(BaseTestCase):

    def testBindCursor(self):
        "test binding in a cursor"
        cursor = self.connection.cursor()
        self.failUnlessEqual(cursor.description, None)
        self.cursor.execute(u"""
                begin
                  open :p_Cursor for select 1 NumberCol from dual;
                end;""",
                p_Cursor = cursor)
        self.failUnlessEqual(cursor.description,
                [ ('NUMBERCOL', cx_Oracle.NUMBER, 127, 2, 0, 0, 1) ])
        self.failUnlessEqual(cursor.fetchall(), [(1.0,)])

    def testBindCursorInPackage(self):
        "test binding in a cursor from a package"
        cursor = self.connection.cursor()
        self.failUnlessEqual(cursor.description, None)
        self.cursor.callproc(u"pkg_TestOutCursors.TestOutCursor", (2, cursor))
        self.failUnlessEqual(cursor.description,
                [ ('INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  ('STRINGCOL', cx_Oracle.STRING, 20, 20, 0, 0, 0) ])
        self.failUnlessEqual(cursor.fetchall(),
                [ (1, 'String 1'), (2, 'String 2') ])

    def testFetchCursor(self):
        "test fetching a cursor"
        self.cursor.execute(u"""
                select
                  IntCol,
                  cursor(select IntCol + 1 from dual) CursorValue
                from TestNumbers
                order by IntCol""")
        size = struct.calcsize('P')
        self.failUnlessEqual(self.cursor.description,
                [ (u'INTCOL', cx_Oracle.NUMBER, 10, 22, 9, 0, 0),
                  (u'CURSORVALUE', cx_Oracle.CURSOR, -1, size, 0, 0, 1) ])
        for i in range(1, 11):
            number, cursor = self.cursor.fetchone()
            self.failUnlessEqual(number, i)
            self.failUnlessEqual(cursor.fetchall(), [(i + 1,)])

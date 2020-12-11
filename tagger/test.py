import unittest
import logging
import chess
import util
import cook
from model import Puzzle
from tagger import logger, read
from chess import parse_square, ROOK

def make(id: str, fen: str, line: str) -> Puzzle:
    return read({ "_id": id, "fen": fen, "line": line })

class TestTagger(unittest.TestCase):

    logger.setLevel(logging.DEBUG)

    def test_attraction(self):
        self.assertFalse(cook.attraction(make("yUM8F",
            "r1bq1rk1/ppp1bppp/2n2n2/4p1B1/4N1P1/3P1N1P/PPP2P2/R2QKB1R w KQ - 1 9",
            "d1d2 f6e4 d3e4 c6d4 e1c1 d4f3 d2d8 e7g5 d8g5 f3g5"
        )))

        self.assertFalse(cook.attraction(make("wFGMa",
            "4r1k1/1R3ppp/1N3n2/1bP5/1P6/3p3P/6P1/3R2K1 w - - 0 28",
            "b6d5 f6d5 b7b5 d5c3 d1d3 c3b5"
        )))

        self.assertTrue(cook.attraction(make("uf4XN",
            "r4rk1/pp3pp1/7p/b2Pn3/4N3/6RQ/P4PPP/q1B1R1K1 b - - 8 26",
            "a5e1 g3g7 g8g7 h3h6 g7g8 e4f6"
        )))

        self.assertTrue(cook.attraction(make("wRDRr", "2kr1b1r/1p1b2pp/p1P1p2n/2P3N1/P4q2/5N2/4BKPP/R2Q3R b - - 2 18", "d7c6 d1d8 c8d8 g5e6 d8c8 e6f4")))

    def test_sacrifice(self):
        self.assertTrue(cook.sacrifice(make("1NHUV", "r1b2rk1/pppp1ppp/2n5/3Q2B1/2B5/2P2N2/P1q3PP/4RK1R b - - 1 14", "d7d6 d5f7 f8f7 e1e8")))
        self.assertFalse(cook.sacrifice(make("1HDGN", "3qr1k1/R4pbp/2p3p1/1p1p4/1P3Q2/2P1P3/3B2P1/7K b - - 0 33", "d8b8 f4f7 g8h8 f7g7")))
        self.assertTrue(cook.sacrifice(make("1PljR", "1R1r2k1/5ppp/p7/3q1P2/2pr1B2/3n2PP/4Q3/5RK1 b - - 4 30", "d3f4 e2e8 d8e8 b8e8")))
        self.assertTrue(cook.sacrifice(make("7frsv", "4r1k1/pb3ppp/1p1b1n2/2pP4/4P1q1/2N5/PBQ2PPP/R4RK1 w - - 0 19", "c2e2 d6h2 g1h2 g4h4 h2g1 f6g4 e2g4 h4g4")))
        self.assertFalse(cook.sacrifice(make("2FSmI", "r2q1rk1/pp3p2/4pn1R/8/3Q4/5N2/PPP2PPb/R5K1 w - - 0 19", "g1h2 d8d4 f3d4 f6g4 h2g3 g4h6")))
        self.assertTrue(cook.sacrifice(make("6UjJO", "r1bqnrk1/pp1n2p1/3bp1N1/3p1p2/2pP1P2/2P1PN1R/PP4PP/R1BQ2K1 b - - 1 15", "f8f6 h3h8 g8f7 f3g5 f7g6 d1h5")))
        self.assertTrue(cook.sacrifice(make("uHVch", "4r3/1b4p1/p7/1p1Pp1kr/4Qp2/1B1R1RP1/PP3P1P/2q3K1 w - - 1 31", "g1g2 h5h2 g2h2 e8h8 e4h7 h8h7 h2g2 c1h1")))
        self.assertFalse(cook.sacrifice(make("51K8X", "r3r1k1/pp1n1pp1/2p3p1/3p4/3PnqPN/2P4P/PPQN1P2/4RRK1 w - - 2 18", "h4g2 f4d2 c2d2 e4d2 e1e8 a8e8")))
        # temporary exchange sac
        self.assertTrue(cook.sacrifice(make("2pqYA", "6k1/p6p/2r2bp1/1pp4r/5P2/3R2P1/P5BP/3R3K b - - 1 29", "c5c4 d3d8 f6d8 d1d8 g8f7 g2c6")))

    def test_defensive(self):
        self.assertFalse(cook.defensive_move(make("6MVFt", "8/2P5/3K4/8/4pk2/2r3p1/R7/8 b - - 0 50", "f4f3 a2a3 c3a3 c7c8q")))
        self.assertFalse(cook.defensive_move(make("5Winv", "6k1/2Q2pp1/p5rp/3P4/2pn3r/5P1q/P1N2RPP/4R1K1 w - - 0 32", "c2d4 h4d4 c7b8 g8h7")))

    def test_check_escape(self):
        self.assertTrue(cook.check_escape(make("i6rNU", "1R6/1P4p1/8/6k1/4K3/1r4pP/8/8 w - - 0 39", "h3h4 g5g4")))

    def test_fork(self):
        self.assertTrue(cook.fork(make("0PQep", "6q1/p6p/6p1/4k3/1P2N3/2B2P2/4K1P1/8 b - - 3 43", "e5d5 e4f6 d5c4 f6g8")))
        self.assertFalse(cook.fork(make("0O5RW", "rnb1k2r/p1B2ppp/4p3/1Bb5/8/4P3/PP1K1PPP/nN4NR b kq - 0 12", "b8d7 b5c6 c8a6 c6a8 c5b4 b1c3")))
        self.assertTrue(cook.fork(make("1NxIN", "r3k2r/p2q1ppp/4pn2/1Qp5/8/4P3/PP1N1PPP/R3K2R w KQkq - 2 16", "b5c5 d7d2 e1d2 f6e4 d2e2 e4c5")))
        self.assertFalse(cook.fork(make("6ppA2", "8/p7/1p6/2p5/P6P/2P2Nk1/1r4P1/4R1K1 w - - 1 39", "f3d2 b2d2 h4h5 d2g2")))
        self.assertFalse(cook.fork(make("bypCs", "rnbq1b1r/p1k1pQp1/2p4p/1p1nP1p1/2pP4/2N3B1/PP3P1P/R3KBNR w KQ - 5 14", "c3d5 d8d5 f7d5 c6d5")))
        self.assertFalse(cook.fork(make("qgSLr", "2r3k1/6p1/p2q1rRp/3pp3/3P1p1R/3Q3P/PP3PP1/6K1 w - - 0 31", "g6f6 d6f6 h4h5 e5e4 d3b3 g7g5 b3d5 f6f7 d5e4 c8c1 g1h2 f7h5")))
        self.assertFalse(cook.fork(make("2eqdQ", "r4rk1/pp2qppp/5p2/1b1p4/1b1Q4/2N1B3/PPP2PPP/2KR3R b - - 7 13", "b4c5 d4c5 e7c5 e3c5")))
        self.assertFalse(cook.fork(make("QNrtc", "r2qr1k1/5p1p/pn3bp1/1p6/3P2bN/1P1B2PP/PB3PQ1/R3R1K1 b - - 0 19", "f6d4 e1e8 d8e8 b2d4")))
        self.assertFalse(cook.fork(make("J72FN", "6k1/7p/3R2p1/8/5p2/P4P2/1P1N2PP/3r1nK1 w - - 0 33", "d2e4 f1d2 g1f2 d2e4")))

    def test_trapped(self):
        self.assertTrue(cook.trapped_piece(make("nPqjh", "r4rk1/pp1nppbp/3p1n2/q4p2/8/N1P1PP2/PP1BB1PP/2RQ1RK1 b - - 0 13", "b7b6 e2b5 a7a6 c3c4 a5a3 b2a3")))
        self.assertFalse(cook.trapped_piece(make("pjqyb", "r1b1k3/1pp4R/3p4/p2P4/2P5/8/PP2pKPP/8 b - - 1 34", "c8f5 h7h8 e8e7 h8a8 e2e1q f2e1")))
        self.assertTrue(cook.trapped_piece(make("pqkqG", "rnb1k2r/ppppqppp/8/2b4n/4P1N1/2N5/PPPP1PPP/R1BQKB1R w KQkq - 3 6", "f2f3 e7h4 g2g3 h5g3 h2g3 h4h1")))
        self.assertFalse(cook.trapped_piece(make("23J63", "2r2rk1/3bbpp1/p2p1n1p/1p1Pp3/4P3/5QNP/PPq2PPN/R1B1R1K1 w - - 6 19", "e1e2 c2d1 h2f1 c8c1 a1c1 d1c1")))
        self.assertFalse(cook.trapped_piece(make("2NQ68", "3qr1k1/p5pp/1p3n2/3p2P1/2rQ4/5B1P/PBb2P2/2R2RK1 w - - 1 21", "f3d5 d8d5 d4d5 f6d5")))

    def test_discovered_attack(self):
        self.assertFalse(cook.discovered_attack(make("0e7Q3", "5rk1/2pqnrpp/p3p1b1/N3P3/1PRPPp2/P4Q2/3B1RPP/6K1 w - - 3 30", "d2f4 f7f4 f3f4 f8f4")))
        self.assertFalse(cook.discovered_attack(make("0ZSP0", "5rk1/3R4/p1p3pp/1p2b3/2P1n2q/4Q2P/PP3PP1/4R1K1 w - - 4 27", "e3e4 h4f2 g1h1 f2f1 e1f1 f8f1")))
        self.assertTrue(cook.discovered_attack(make("01Y7w", "r2q1rk1/pppb1pbp/2n1pnp1/1BPpB3/3P4/4PN2/PP3PPP/RN1QK2R w KQ - 3 9", "e1g1 c6e5 d4e5 d7b5")))
        self.assertTrue(cook.discovered_attack(make("07jQK", "r4rk1/p1p1qppp/3b4/4n3/Q7/2NP4/PP3PPP/R1B2RK1 w - - 0 16", "f1e1 e5f3 g2f3 e7e1")))
        self.assertTrue(cook.discovered_attack(make("0VlKP", "5r2/6k1/8/p1p1p1p1/Pp1p2P1/1P1PnN1P/2P1KR2/8 w - - 3 38", "f3e5 f8e8 e5c6 e3g4 e2f1 g4f2")))
        self.assertFalse(cook.discovered_attack(make("m3h3k", "2r3k1/1r2pp1p/bqNp2p1/3P4/1p2P3/4bN2/1P4PP/2RQR2K w - - 0 24", "c6e7 b7e7 c1c8 a6c8")))
        self.assertFalse(cook.discovered_attack(make("PsryZ", "4r2k/6pp/1R6/1pq5/8/P4QPP/1P3P1K/8 w - - 3 41", "f3c6 c5f2 c6g2 f2b6")))

    def test_deflection(self):
        self.assertTrue(cook.deflection(make("25Qpt", "r1bqkbnr/pp3p1p/6p1/2pBp3/4P3/2P1B3/PP3PPP/RN1QK2R b KQkq - 0 9", "g8f6 d5f7 e8f7 d1d8")))
        self.assertFalse(cook.deflection(make("0EgUL", "rnb1k2r/pppp2p1/4p2p/5p2/1q1Pn2P/2NQPN2/PPP2PP1/R3KB1R w KQkq - 1 9", "a2a3 b4b2 a1b1 b2c3 d3c3 e4c3")))
        self.assertFalse(cook.deflection(make("08vBP", "8/1R4p1/p5rp/4bN2/5kP1/2P4K/PP6/8 b - - 0 40", "g6g4 b7b4 f4f5 b4g4")))
        self.assertFalse(cook.deflection(make("0ZSP0", "5rk1/3R4/p1p3pp/1p2b3/2P1n2q/4Q2P/PP3PP1/4R1K1 w - - 4 27", "e3e4 h4f2 g1h1 f2f1 e1f1 f8f1")))
        self.assertFalse(cook.deflection(make("3J2Nl", "r2q2k1/pp4bp/3pnppn/3N4/4Pp1B/7P/PPPQ2P1/R4RK1 w - - 0 19", "d5f4 e6f4 f1f4 g6g5 d2d5 g8h8 f4f2 g5h4")))
        self.assertFalse(cook.deflection(make("3051j", "r2k2r1/1b2nQb1/1p2p2p/p3Pp2/2P4q/P6P/NP2R1PN/2R4K b - - 0 26", "h4d4 a2c3 g8f8 f7g7 f8g8 g7h6")))
        self.assertFalse(cook.deflection(make("0VlKP", "5r2/6k1/8/p1p1p1p1/Pp1p2P1/1P1PnN1P/2P1KR2/8 w - - 3 38", "f3e5 f8e8 e5c6 e3g4 e2f1 g4f2")))
        self.assertTrue(cook.deflection(make("7ycL5", "r1bqkb1r/4pp1p/p1pp1np1/4P3/P1B5/2N5/1PP2PPP/R1BQK2R b KQkq - 0 9", "d6e5 c4f7 e8f7 d1d8")))
        self.assertTrue(cook.deflection(make("oGLtH", "8/8/PR4K1/8/5k1P/r7/4p3/8 w - - 0 52", "b6e6 a3a6 e6a6 e2e1q")))
        self.assertTrue(cook.deflection(make("bZQyl", "8/R4pk1/6p1/P6p/3n3P/5PK1/r4NP1/8 w - - 3 43", "a5a6 d4f5 g3h2 a2f2")))

    def test_skewer(self):
        self.assertTrue(cook.skewer(make("29HGS", "3r4/6p1/5r1p/7k/3N1P2/3K2P1/3R4/3R4 w - - 1 50", "d2e2 d8d4 d3d4 f6d6 d4e5 d6d1")))

    def test_interference(self):
        self.assertFalse(cook.interference(make("2t6Xz", "6k1/1b1q1pbp/4pnp1/2Pp4/rp1P1P2/3BPRNP/4Q1P1/4B1K1 b - - 1 26", "f6e4 d3b5 b7c6 b5a4")))
        self.assertTrue(cook.interference(make("QssMO", "r5k1/ppp2r2/3p3p/3Pp3/1P2N1bb/R5N1/1P3P1K/6R1 b - - 5 25", "g4f3 g3f5 g8h7 a3f3")))

    # def test_clearance(self):
    #     self.assertTrue(cook.clearance(make("iq12Z", "1R6/1P2r1pk/7p/6pr/3Pp3/1KP1R3/8/8 b - - 0 55", "g5g4 b8h8 h7h8 b7b8q")))

    def test_x_ray(self):
        self.assertTrue(cook.x_ray(make("fo0LG", "5R2/8/p1p4p/1p1p2k1/6r1/1P2P1r1/P1PKR3/8 b - - 3 33", "g3g2 f8g8 g5f6 e2g2 g4g2 g8g2")))

    def test_quiet_move(self):
        self.assertFalse(cook.quiet_move(make("SxOf2", "7r/3k4/1P3p2/1K1Pp1p1/2N1P1P1/8/8/8 b - - 2 49", "h8h4 b6b7 h4h1 b7b8n")))

    def test_pin_prevents_attack(self):
        # pins the queen from attacking the g2 pawn
        self.assertTrue(cook.pin_prevents_attack(make("P2D4h", "2k5/p7/bpq1p3/8/2PP2P1/1K2P1p1/4Q1P1/8 b - - 4 36", "a6c4 e2c4 c6c4 b3c4")))
        self.assertTrue(cook.pin_prevents_attack(make("aJPsJ", "r2q1r1k/pp3pp1/2p2n1p/3PB2b/3P4/1B5P/P1PQ1PP1/R3R1K1 b - - 0 18", "f6d5 d2h6 h8g8 h6g7")))
        self.assertFalse(cook.pin_prevents_attack(make("9CkIh", "r4r2/pp3pkp/2p5/3pPp1q/3p1P2/3Q1R2/PPP3PP/R5K1 b - - 3 18", "c6c5 f3h3 h5g6 h3g3 g7h8 g3g6")))
        self.assertFalse(cook.pin_prevents_attack(make("0CR44", "r2q4/4b1kp/6p1/2ppPr2/3P4/2P2N2/P4RQP/R5K1 w - - 0 27", "f3d2 f5g5 d2f3 g5g2")))
        self.assertFalse(cook.pin_prevents_attack(make("NCP9T", "1kr5/p3R3/7p/5Pp1/6P1/6K1/PP1R1P1P/6r1 w - - 1 32", "g3h3 h6h5 g4h5 c8h8 e7e8 h8e8")))
        # relative pin
        # self.assertTrue(cook.pin_prevents_attack(make("spQRx", "8/8/5K2/5p2/6k1/3R2Pr/8/8 w - - 16 56", "f6e5 f5f4")))

    def test_pin_prevents_escape(self):
        self.assertFalse(cook.pin_prevents_escape(make("P2D4h", "2k5/p7/bpq1p3/8/2PP2P1/1K2P1p1/4Q1P1/8 b - - 4 36", "a6c4 e2c4 c6c4 b3c4")))
        self.assertFalse(cook.pin_prevents_escape(make("aJPsJ", "r2q1r1k/pp3pp1/2p2n1p/3PB2b/3P4/1B5P/P1PQ1PP1/R3R1K1 b - - 0 18", "f6d5 d2h6 h8g8 h6g7")))
        self.assertTrue(cook.pin_prevents_escape(make("9CkIh", "r4r2/pp3pkp/2p5/3pPp1q/3p1P2/3Q1R2/PPP3PP/R5K1 b - - 3 18", "c6c5 f3h3 h5g6 h3g3 g7h8 g3g6")))
        self.assertTrue(cook.pin_prevents_escape(make("0CR44", "r2q4/4b1kp/6p1/2ppPr2/3P4/2P2N2/P4RQP/R5K1 w - - 0 27", "f3d2 f5g5 d2f3 g5g2")))
        self.assertFalse(cook.pin_prevents_escape(make("NCP9T", "1kr5/p3R3/7p/5Pp1/6P1/6K1/PP1R1P1P/6r1 w - - 1 32", "g3h3 h6h5 g4h5 c8h8 e7e8 h8e8")))
        self.assertFalse(cook.pin_prevents_escape(make("6Jh1x", "2r5/1KP5/8/4k3/7p/7P/4p3/2R5 b - - 1 49", "c8e8 c1e1 e5f4 e1e2 e8e2 c7c8q")))

    def test_hanging_piece(self):
        self.assertTrue(cook.hanging_piece(make("069il", "r2qr1k1/1p3ppp/p1p2nb1/8/4P3/1P5P/PBQN1PP1/R3R1K1 w - - 1 17", "c2c4 d8d2 b2f6 g7f6")))
        self.assertTrue(cook.hanging_piece(make("cWlcD", "8/p4p2/2p2Pk1/1p1p2pp/1P4P1/2P4P/2r2R2/5K2 b - - 1 40", "h5g4 f2c2")))

    def test_advanced_pawn(self):
        self.assertFalse(cook.advanced_pawn(make("C3gv2", "4r3/R1p2k2/3p1pp1/2r2p1p/1pN2Pn1/1P2PKP1/2P3P1/4R3 b - - 3 39", "d6d5 c4d6 f7e7 d6e8")))
        self.assertFalse(cook.advanced_pawn(make("JgJgO", "1R6/6kp/4Pp1q/3P4/R1P5/P5pP/6P1/7K w - - 1 34", "e6e7 h6c1")))
        self.assertTrue(cook.advanced_pawn(make("PKGhN", "2R5/2P2kpp/8/1p4b1/4n3/P6P/2p2PPK/2B5 b - - 0 41", "g5c1 c8f8 f7f8 c7c8q")))
        self.assertFalse(cook.advanced_pawn(make("qqs1r", "6r1/pppq3k/2np2np/8/3P2pB/N1PR1p2/PP2QPBN/6K1 w - - 0 33", "g2f3 g4f3 e2f1 g6h4")))

    def test_rook_endgame(self):
        self.assertFalse(cook.piece_endgame(make("qgryh", "8/p5KP/k7/6R1/6P1/1p6/8/7r w - - 0 44", "h7h8q h1h8 g7h8 b3b2 g5h5 b2b1q"), ROOK))
        self.assertFalse(cook.piece_endgame(make("p5BrZ", "8/4R1P1/8/3r4/6K1/8/4p3/3k4 b - - 0 62", "e2e1q e7e1 d1e1 g7g8q"), ROOK))
        self.assertTrue(cook.piece_endgame(make("j0qyE", "8/5p2/5k2/p4p2/8/1PPp1R2/r7/3K2R1 w - - 1 36", "f3d3 a2a1 d1d2 a1g1"), ROOK))
        self.assertFalse(cook.piece_endgame(make("Zjk3J", "8/pppk4/3p4/3P1p1p/PP3Rr1/4PpPK/5P2/8 w - - 5 36", "f4g4 h5g4 h3h4 c7c5 d5c6 b7c6 h4g5 d7e6"), ROOK))

    def test_intermezzo(self):
        self.assertTrue(cook.intermezzo(make("11pYZ", "8/5rpk/7p/8/3Q4/B4NKP/R2n2P1/5q2 b - - 3 42", "d2f3 d4e4 g7g6 g2f3")))
        self.assertTrue(cook.intermezzo(make("1E2zU", "6k1/4rpp1/3r3p/p2N4/PbB5/1Pq2Q1P/R2p1PP1/3R2K1 b - - 8 31", "c3f3 d5e7 g8f8 g2f3")))
        self.assertFalse(cook.intermezzo(make("1KWbk", "3r2k1/p3bqpp/2b1p3/2p2p2/8/2PNB1QP/PP3PP1/R5K1 w - - 2 26", "d3c5 f5f4 e3f4 e7c5")))
        self.assertFalse(cook.intermezzo(make("21ViC", "4b2r/r6k/6p1/3BQ1Rn/3P1P1P/p1qN4/2P5/2K5 b - - 0 33", "c3c7 g5h5 g6h5 d5e4 e8g6 e5h5 h7g8 h5g6")))

    def test_back_rank_mate(self):
        self.assertTrue(cook.back_rank_mate(make("tMEri", "5r1k/4q1p1/p2pP2p/1p6/1P2Q3/PB6/1BP3PP/6K1 w - - 1 27", "e4g6 e7a7 b2d4 a7d4 g1h1 f8f1")))
        self.assertFalse(cook.back_rank_mate(make("08VjT", "3r2k1/1bQ3p1/p2p3p/3qp1b1/1p6/1P1B4/P1P3PP/1K3R2 b - - 4 25", "d5c6 c7f7 g8h8 f7f8 d8f8 f1f8")))
        self.assertTrue(cook.back_rank_mate(make("LYKY0", "r5k1/pQ3ppp/8/8/B1pp4/4q3/PP5P/5R1K b - - 0 26", "a8d8 b7f7 g8h8 f7f8 d8f8 f1f8")))
        self.assertFalse(cook.back_rank_mate(make("ABCL2", "3r2k1/1b4pp/1p2pr2/p5N1/8/PP2n1P1/1BR2bBP/4R2K w - - 1 27", "b2f6 b7g2")))

    def side_attack(self):
        self.assertFalse(cook.kingside_attack(make("KnAMG", "6k1/1p4p1/p1p4p/3p1rq1/3Pp1N1/2P5/PP2K1Q1/5R2 w - - 0 39", "g4h6 g7h6 g2g5 f5g5")))

class TestUtil(unittest.TestCase):

    def test_trapped(self):
        self.assertFalse(util.is_trapped(
            chess.Board("q3k3/7p/8/4N2q/3PP3/4B3/8/4K2R b - - 0 1"), parse_square("h5")
        ))
        self.assertTrue(util.is_trapped(
            chess.Board("q3k3/7p/8/4N2q/3PP3/4B3/7R/4K2R b - - 0 1"), parse_square("h5")
        ))
        self.assertFalse(util.is_trapped(
            chess.Board("q3k3/7p/8/4N2b/3PP3/4B3/7R/4K2R b - - 0 1"), parse_square("h5")
        ))
        self.assertFalse(util.is_trapped(
            chess.Board("4k3/7p/8/4N2q/3PP2p/4B3/8/4K3 b - - 0 1"), parse_square("h5")
        ))
        self.assertTrue(util.is_trapped(
            chess.Board("8/3P4/8/4N2b/7p/6N1/8/4K3 b - - 0 1"), parse_square("h5")
        ))

if __name__ == '__main__':
    unittest.main()

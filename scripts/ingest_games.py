from chess_coach.database.connection import engine
from chess_coach.database.models import Game
from sqlalchemy.orm import Session


game = Game(
    white_player="Pawan",
    black_player="h8848",
    result="1-0",
    event="Chess.com",
    pgn='''1. e4 e6 2. d3 d5 3. Nd2 Nf6 4. Ngf3 Be7 5. g3 c5 6. Bg2 Nc6 7. O-O O-O 8. e5
        Nd7 9. Re1 Qc7 10. Qe2 a6 11. Nf1 b5 12. h4 Bb7 13. h5 h6 14. N1h2 Qd8 15. Ng4
        Kh7 16. Bf4 Rc8 17. Qd2 Nd4 18. Bxh6 Nxf3+ 19. Bxf3 gxh6 20. Qxh6+ Kg8 21. Qd2
        Bg5 22. Qe2 Qc7 23. Bg2 d4 24. f4 Bxg2 25. Qxg2 Bh6 26. Nxh6+ Kh7 27. Ng4 Rg8
        28. Qe4+ Kh8 29. Qf3 Rg7 30. Kh2 Rcg8 31. Nf2 Rxg3 32. Qxg3 Rxg3 33. Kxg3 c4 34.
        Rac1 Nb6 35. Ne4 Nd5 36. Rg1 Qc8 37. Kf3 Ne7 38. Rg5 cxd3 39. Nd6 Qc6+ 40. Kf2
        Nf5 41. Nxf7+ Kh7 42. h6 dxc2 43. Rcg1'''
)


with Session(engine) as session:
    session.add(game)
    session.commit()

    print(f"Game inserted with ID: {game.game_id}")
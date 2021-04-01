import tiledb
from commands.root import root

from click.testing import CliRunner
import os
import numpy as np
import pandas as pd
import pytest


@pytest.fixture(autouse=True, scope="session")
def create_test_simple_csv(temp_rootdir):
    """
    Create a simple dense test array.
    """
    path = os.path.abspath(os.path.join(temp_rootdir, "simple.csv"))

    with open(path, mode="w") as csv_input:
        csv_input.write(
            (
                "a,b,c,date\n"
                '1,"text",3.4,Mar/02/2021\n'
                '2,"hello",1.234,Apr/07/2021\n'
                '3,"goodbye",111.232,Dec/17/2021\n'
                '4,"world",123123.12,Jul/21/2021\n'
                '10,"raisins",14.232,Nov/09/2021\n'
            )
        )

    expected_output = pd.DataFrame(
        {
            "a": [1, 2, 3, 4, 10],
            "b": ["text", "hello", "goodbye", "world", "raisins"],
            "c": [3.400, 1.234, 111.232, 123123.120, 14.232],
            "date": [
                "Mar/02/2021",
                "Apr/07/2021",
                "Dec/17/2021",
                "Jul/21/2021",
                "Nov/09/2021",
            ],
        }
    )

    return ("simple", expected_output)


class TestCSV:
    def test(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri]
        """
        test_name, expected_output = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert pd.DataFrame.equals(array.df[:], expected_output)

    def test_sparse(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --sparse=True
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_sparse.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--sparse=True"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.sparse == True

    def test_dense(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --sparse=False
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_dense.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--sparse=False"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.sparse == False

    def test_duplicates(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --allows-duplicates=(False|True)
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")

        uri = os.path.join(temp_rootdir, "test_no_duplicates.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=True",
                "--allows-duplicates=False",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.allows_duplicates == False

        uri = os.path.join(temp_rootdir, "test_allows_duplicates.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=True",
                "--allows-duplicates=True",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.allows_duplicates == True

    def test_capacity(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --capacity=<int>
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_capacity.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--capacity=123456"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.capacity == 123456

    def test_cell_order(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --cell-order=(row-major|col-major|global)
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_cell_order.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--cell-order=global"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.cell_order == "global"

    def test_full_domain(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --full-domain
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_full_domain.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--full-domain=True"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            dim = array.schema.domain.dim("__tiledb_rows")
            assert dim.domain[0] == np.iinfo(np.uint64).min
            assert dim.domain[1] == np.iinfo(np.uint64).max - dim.tile

    def test_date_spec(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --date-spec <column> <datetime format spec>
        """
        test_name, expected_output = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_date_spec.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "-d", "date", "%b/%d/%Y"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert pd.DataFrame.equals(
                array.query(["date"]).df[:],
                pd.DataFrame(pd.to_datetime(expected_output["date"])),
            )

    def test_mode_schema_only(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --mode=(ingest|schema_only|append)
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_mode_schema_only.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=True",
                "--mode=schema_only",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.query(use_arrow=False).df[0].empty

    def test_row_start_idx(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --row-start-idx=<int>
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_row_start_idx.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=False",
                "--row-start-idx=5",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.df[:].index.to_numpy()[0] == 5
            assert array.df[:].index.to_numpy()[-1] == 9

    def test_cell_order(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --cell-order=(row-major|col-major|global)
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_cell_order.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--cell-order=col-major"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.cell_order == "col-major"

    def test_tile_int(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --tile=<int>
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_tile_int.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--tile=2"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.domain.dim("__tiledb_rows").tile == 2

    def test_tile_with_attr(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --tile=<attr>:<int>
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_tile_with_attr.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--tile=__tiledb_rows:2"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.domain.dim("__tiledb_rows").tile == 2

    def test_timestamp(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --timestamp=<int>
        """
        test_name, expected_output = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_timestamp.tdb")

        runner = CliRunner()

        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=True",
                "--mode=ingest",
                "--timestamp=1",
            ],
        )

        assert result.exit_code == 0

        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--sparse=True",
                "--mode=append",
                "--timestamp=2",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri, timestamp=1) as array:
            assert pd.DataFrame.equals(
                array.df[:].loc[:, array.df[:].columns != "__tiledb_rows"],
                expected_output,
            )

        with tiledb.open(uri, timestamp=2) as array:
            assert pd.DataFrame.equals(
                array.df[:].loc[:, array.df[:].columns != "__tiledb_rows"],
                expected_output.append(expected_output, ignore_index=True),
            )

    def test_attr_filters(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --attr-filters <filter name>,<filter name>,...
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_attr_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--attr-filters", "GzipFilter=9"],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.attr("a").filters.nfilters == 1
            assert array.schema.attr("a").filters[0] == tiledb.GzipFilter(9)

            assert array.schema.attr("b").filters.nfilters == 1
            assert array.schema.attr("b").filters[0] == tiledb.GzipFilter(9)

            assert array.schema.attr("c").filters.nfilters == 1
            assert array.schema.attr("c").filters[0] == tiledb.GzipFilter(9)

            assert array.schema.attr("date").filters.nfilters == 1
            assert array.schema.attr("date").filters[0] == tiledb.GzipFilter(9)

    def test_attr_filters_multi(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --attr-filters <attr name>:<filter name>,<filter name>,...
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_attr_filters_multi.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--attr-filters",
                "a:LZ4Filter=10,BitShuffleFilter",
                "--attr-filters",
                "b:DoubleDeltaFilter,PositiveDeltaFilter=3",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.attr("a").filters.nfilters == 2
            assert array.schema.attr("a").filters[0] == tiledb.LZ4Filter(10)
            assert array.schema.attr("a").filters[1] == tiledb.BitShuffleFilter()

            assert array.schema.attr("b").filters.nfilters == 2
            assert array.schema.attr("b").filters[0] == tiledb.DoubleDeltaFilter()
            assert array.schema.attr("b").filters[1] == tiledb.PositiveDeltaFilter(3)

            assert array.schema.attr("c").filters.nfilters == 0

            assert array.schema.attr("date").filters.nfilters == 0

    def test_coords_filters(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --coords-filters <filter name>,<filter name>,...
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_coords_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            [
                "convert-from",
                "csv",
                input_path,
                uri,
                "--coords-filters",
                "GzipFilter=9",
            ],
        )

        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.coords_filters.nfilters == 1
            assert array.schema.coords_filters[0] == tiledb.GzipFilter(9)

    def test_dim_filters(self, temp_rootdir, create_test_simple_csv):
        """
        Test for command

            tiledb convert_from [csv_file] [uri] --dim-filters <filter name>,<filter name>,...
        """
        test_name, _ = create_test_simple_csv
        input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
        uri = os.path.join(temp_rootdir, "test_dim_filters.tdb")

        runner = CliRunner()
        result = runner.invoke(
            root,
            ["convert-from", "csv", input_path, uri, "--dim-filters", "GzipFilter=9"],
        )
        assert result.exit_code == 0

        with tiledb.open(uri) as array:
            assert array.schema.domain.dim(0).filters.nfilters == 1
            assert array.schema.domain.dim(0).filters[0] == tiledb.GzipFilter(9)

    # # @pytest.mark.skip(reason="TODO implement full test")
    # def test_sep(self, temp_rootdir, create_test_simple_csv):
    #     """
    #     Test for command

    #         tiledb convert_from [csv_file] [uri] -s <str>
    #     """
    #     test_name, _ = create_test_simple_csv
    #     input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
    #     uri = os.path.join(temp_rootdir, "test_sep.tdb")

    #     runner = CliRunner()
    #     result = runner.invoke(
    #         root, ["convert-from", "csv", input_path, uri, "--sep=a"]
    #     )

    #     assert result.exit_code == 0
    #     with tiledb.open(uri) as array:
    #         print(array.df[:])

    # @pytest.mark.skip("TODO implement full test")
    # def test_header(self, temp_rootdir, create_test_simple_csv):
    #     """
    #     Test for command

    #         tiledb convert_from [csv_file] [uri] -h <int>
    #     """
    #     test_name, _ = create_test_simple_csv
    #     input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
    #     uri = os.path.join(temp_rootdir, "test_header.tdb")

    #     runner = CliRunner()
    #     result = runner.invoke(
    #         root, ["convert-from", "csv", input_path, uri, "--header=2"]
    #     )

    #     assert result.exit_code == 0
    #     with tiledb.open(uri) as array:
    #         print(array.df[:])

    # # @pytest.mark.skip("TODO implement full test")
    # def test_names(self, temp_rootdir, create_test_simple_csv):
    #     """
    #     Test for command

    #         tiledb convert_from [csv_file] [uri] -N <column name>
    #     """
    #     test_name, _ = create_test_simple_csv
    #     input_path = os.path.join(temp_rootdir, f"{test_name}.csv")
    #     uri = os.path.join(temp_rootdir, "test_names.tdb")

    #     runner = CliRunner()
    #     result = runner.invoke(
    #         root,
    #         [
    #             "convert-from",
    #             "csv",
    #             input_path,
    #             uri,
    #             "-h",
    #             0,
    #             "-N",
    #             "d",
    #             "-N",
    #             "c",
    #             "-N",
    #             "b",
    #             "-N",
    #             "a",
    #         ],
    #     )

    #     assert result.exit_code == 0
    #     with tiledb.open(uri) as array:
    #         print(array.df[:])
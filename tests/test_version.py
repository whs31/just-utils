from pathlib import Path
import semver
import just_utils as ju


def test_version():
    root = Path(__file__).parent / "test_data"
    ju.show_version(root)
    ju.patch_version(semver.Version(1, 2, 3), root)
    ju.show_version(root)
    ju.patch_version(semver.Version(2, 8, 12), root)
    ju.show_version(root)


if __name__ == "__main__":
    test_version()